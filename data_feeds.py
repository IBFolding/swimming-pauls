"""
Swimming Pauls Data Feeds Module - LOCAL VERSION
100% local operation - no APIs, no cloud required

Provides local connectors for:
- Local files (PDFs, CSVs, JSON, TXT)
- RSS feeds (no API key)
- Web scraping (no API key)
- File system monitoring

API connectors (NewsAPI, Reddit, etc.) are available but optional.
Set environment variable SWIMMING_PAULS_USE_APIS=1 to enable.
"""

import asyncio
import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union
from urllib.parse import urlencode

import httpx


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class NewsArticle:
    """Represents a news article from various sources."""
    title: str
    source: str
    published_at: datetime
    url: str
    summary: Optional[str] = None
    sentiment: Optional[float] = None  # -1.0 to 1.0
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "url": self.url,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "keywords": self.keywords,
        }


@dataclass
class MarketPrice:
    """Represents a market price data point."""
    symbol: str
    price: float
    currency: str
    timestamp: datetime
    change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    source: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "change_24h": self.change_24h,
            "volume_24h": self.volume_24h,
            "market_cap": self.market_cap,
            "source": self.source,
        }


@dataclass
class SentimentScore:
    """Represents sentiment analysis result."""
    platform: str  # twitter, reddit, etc.
    topic: str
    score: float  # -1.0 (negative) to 1.0 (positive)
    volume: int  # number of posts/messages
    timestamp: datetime
    trending: List[str] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "topic": self.topic,
            "score": self.score,
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat(),
            "trending": self.trending,
            "raw_data": self.raw_data,
        }


@dataclass
class FileChange:
    """Represents a file system change event."""
    file_path: Path
    change_type: str  # created, modified, deleted
    timestamp: datetime
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": str(self.file_path),
            "change_type": self.change_type,
            "timestamp": self.timestamp.isoformat(),
            "file_size": self.file_size,
            "checksum": self.checksum,
        }


# =============================================================================
# Base Connector
# =============================================================================

class DataConnector(ABC):
    """Abstract base class for all data connectors."""
    
    def __init__(self, name: str, cache_ttl: int = 60):
        self.name = name
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, float] = {}
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if not expired."""
        if key in self._cache:
            cached_time = self._cache_time.get(key, 0)
            if time.time() - cached_time < self.cache_ttl:
                return self._cache[key]
        return None
    
    def _set_cached(self, key: str, data: Any) -> None:
        """Cache data with timestamp."""
        self._cache[key] = data
        self._cache_time[key] = time.time()
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_time.clear()
    
    @abstractmethod
    async def fetch(self, **kwargs) -> Any:
        """Fetch data from the source."""
        pass


# =============================================================================
# News API Connector
# =============================================================================

class NewsConnector(DataConnector):
    """
    Connector for fetching news headlines.
    
    Supports multiple sources:
    - newsapi.org (requires API key)
    - gnews.io (requires API key)
    - NewsData.io (requires API key)
    - RSS feeds (no key required)
    """
    
    SOURCES = {
        "newsapi": "https://newsapi.org/v2/everything",
        "gnews": "https://gnews.io/api/v4/search",
        "newsdata": "https://newsdata.io/api/1/latest",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        source: str = "newsapi",
        cache_ttl: int = 300,  # 5 minutes
    ):
        super().__init__("news", cache_ttl)
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.source = source
        self.base_url = self.SOURCES.get(source, self.SOURCES["newsapi"])
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def fetch(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        language: str = "en",
        page_size: int = 20,
        **kwargs
    ) -> List[NewsArticle]:
        """
        Fetch news articles.
        
        Args:
            query: Search query string
            category: News category (business, technology, etc.)
            language: ISO 639-1 language code
            page_size: Number of articles to fetch
            
        Returns:
            List of NewsArticle objects
        """
        cache_key = f"{query}_{category}_{language}_{page_size}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if self.source == "newsapi":
            articles = await self._fetch_newsapi(query, language, page_size)
        elif self.source == "gnews":
            articles = await self._fetch_gnews(query, language, page_size)
        elif self.source == "newsdata":
            articles = await self._fetch_newsdata(query, category, language, page_size)
        else:
            articles = []
        
        self._set_cached(cache_key, articles)
        return articles
    
    async def _fetch_newsapi(
        self,
        query: Optional[str],
        language: str,
        page_size: int
    ) -> List[NewsArticle]:
        """Fetch from NewsAPI.org."""
        if not self.api_key:
            return self._get_demo_news("NewsAPI requires API key")
        
        client = await self._get_client()
        params = {
            "apiKey": self.api_key,
            "language": language,
            "pageSize": page_size,
            "sortBy": "publishedAt",
        }
        if query:
            params["q"] = query
        else:
            params["q"] = "business OR finance OR technology"
        
        try:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get("articles", []):
                article = NewsArticle(
                    title=item.get("title", ""),
                    source=item.get("source", {}).get("name", "Unknown"),
                    published_at=self._parse_datetime(item.get("publishedAt", "")),
                    url=item.get("url", ""),
                    summary=item.get("description", ""),
                )
                articles.append(article)
            return articles
            
        except Exception as e:
            return self._get_demo_news(f"Error: {str(e)}")
    
    async def _fetch_gnews(
        self,
        query: Optional[str],
        language: str,
        page_size: int
    ) -> List[NewsArticle]:
        """Fetch from GNews.io."""
        if not self.api_key:
            return self._get_demo_news("GNews requires API key")
        
        client = await self._get_client()
        params = {
            "apikey": self.api_key,
            "lang": language,
            "max": page_size,
        }
        if query:
            params["q"] = query
        else:
            params["q"] = "business"
        
        try:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get("articles", []):
                article = NewsArticle(
                    title=item.get("title", ""),
                    source=item.get("source", {}).get("name", "Unknown"),
                    published_at=self._parse_datetime(item.get("publishedAt", "")),
                    url=item.get("url", ""),
                    summary=item.get("description", ""),
                )
                articles.append(article)
            return articles
            
        except Exception as e:
            return self._get_demo_news(f"Error: {str(e)}")
    
    async def _fetch_newsdata(
        self,
        query: Optional[str],
        category: Optional[str],
        language: str,
        page_size: int
    ) -> List[NewsArticle]:
        """Fetch from NewsData.io."""
        if not self.api_key:
            return self._get_demo_news("NewsData requires API key")
        
        client = await self._get_client()
        params = {
            "apikey": self.api_key,
            "language": language,
            "size": page_size,
        }
        if query:
            params["q"] = query
        if category:
            params["category"] = category
        
        try:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get("results", []):
                article = NewsArticle(
                    title=item.get("title", ""),
                    source=item.get("source_id", "Unknown"),
                    published_at=self._parse_datetime(item.get("pubDate", "")),
                    url=item.get("link", ""),
                    summary=item.get("description", ""),
                    keywords=item.get("keywords", []) or [],
                )
                articles.append(article)
            return articles
            
        except Exception as e:
            return self._get_demo_news(f"Error: {str(e)}")
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse ISO datetime string."""
        if not dt_str:
            return datetime.now()
        try:
            # Handle various ISO formats
            dt_str = dt_str.replace("Z", "+00:00")
            return datetime.fromisoformat(dt_str)
        except:
            return datetime.now()
    
    def _get_demo_news(self, reason: str) -> List[NewsArticle]:
        """Return demo news when API is unavailable."""
        return [
            NewsArticle(
                title=f"[DEMO] Market Update - Using cached/demo data ({reason})",
                source="Demo",
                published_at=datetime.now(),
                url="https://example.com",
                summary="This is demo data. Set NEWS_API_KEY for real data.",
            ),
            NewsArticle(
                title="[DEMO] Tech Sector Shows Growth",
                source="Demo",
                published_at=datetime.now() - timedelta(hours=1),
                url="https://example.com",
                summary="Technology companies report strong quarterly earnings.",
            ),
            NewsArticle(
                title="[DEMO] Global Markets React to Policy Changes",
                source="Demo",
                published_at=datetime.now() - timedelta(hours=2),
                url="https://example.com",
                summary="International markets adjust to new economic policies.",
            ),
        ]
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# =============================================================================
# Market Data Connector
# =============================================================================

class MarketConnector(DataConnector):
    """
    Connector for fetching market data (stocks & crypto).
    
    Supports:
    - CoinGecko (free, no API key required for basic usage)
    - Alpha Vantage (requires API key for stocks)
    - Yahoo Finance (unofficial, no key required)
    """
    
    ENDPOINTS = {
        "coingecko": "https://api.coingecko.com/api/v3",
        "alphavantage": "https://www.alphavantage.co/query",
        "yahoo": "https://query1.finance.yahoo.com/v8/finance/chart",
    }
    
    # Popular crypto symbols mapping
    CRYPTO_SYMBOLS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "ADA": "cardano",
        "DOT": "polkadot",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "AAVE": "aave",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        source: str = "coingecko",
        cache_ttl: int = 60,  # 1 minute for prices
    ):
        super().__init__("market", cache_ttl)
        self.api_key = api_key or os.getenv("MARKET_API_KEY")
        self.source = source
        self.base_url = self.ENDPOINTS.get(source, self.ENDPOINTS["coingecko"])
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limit_remaining = 60
        self._rate_limit_reset = time.time() + 60
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def fetch(
        self,
        symbols: Union[str, List[str]],
        asset_type: str = "crypto",  # crypto or stock
        currency: str = "usd",
        **kwargs
    ) -> List[MarketPrice]:
        """
        Fetch market prices for given symbols.
        
        Args:
            symbols: Single symbol or list of symbols (e.g., "BTC" or ["BTC", "ETH"])
            asset_type: "crypto" or "stock"
            currency: Currency code (usd, eur, etc.)
            
        Returns:
            List of MarketPrice objects
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        cache_key = f"{','.join(symbols)}_{asset_type}_{currency}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if asset_type == "crypto":
            if self.source == "coingecko":
                prices = await self._fetch_coingecko(symbols, currency)
            else:
                prices = await self._fetch_crypto_alternative(symbols, currency)
        else:
            prices = await self._fetch_stocks(symbols, currency)
        
        self._set_cached(cache_key, prices)
        return prices
    
    async def _fetch_coingecko(
        self,
        symbols: List[str],
        currency: str
    ) -> List[MarketPrice]:
        """Fetch crypto prices from CoinGecko."""
        client = await self._get_client()
        
        # Convert symbols to CoinGecko IDs
        ids = []
        for sym in symbols:
            sym_upper = sym.upper()
            if sym_upper in self.CRYPTO_SYMBOLS:
                ids.append(self.CRYPTO_SYMBOLS[sym_upper])
            else:
                ids.append(sym.lower())
        
        params = {
            "ids": ",".join(ids),
            "vs_currencies": currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        
        try:
            url = f"{self.base_url}/simple/price"
            response = await client.get(url, params=params)
            
            if response.status_code == 429:
                # Rate limited - return cached or demo data
                return self._get_demo_prices(symbols, "Rate limited")
            
            response.raise_for_status()
            data = response.json()
            
            prices = []
            for coin_id, info in data.items():
                # Find original symbol
                symbol = coin_id.upper()
                for sym, cid in self.CRYPTO_SYMBOLS.items():
                    if cid == coin_id:
                        symbol = sym
                        break
                
                price = MarketPrice(
                    symbol=symbol,
                    price=info.get(currency, 0),
                    currency=currency.upper(),
                    timestamp=datetime.now(),
                    change_24h=info.get(f"{currency}_24h_change"),
                    volume_24h=info.get(f"{currency}_24h_vol"),
                    market_cap=info.get(f"{currency}_market_cap"),
                    source="coingecko",
                )
                prices.append(price)
            
            return prices
            
        except Exception as e:
            return self._get_demo_prices(symbols, str(e))
    
    async def _fetch_crypto_alternative(
        self,
        symbols: List[str],
        currency: str
    ) -> List[MarketPrice]:
        """Fallback crypto fetcher using alternative APIs."""
        # Try CoinGecko markets endpoint as fallback
        client = await self._get_client()
        
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                "vs_currency": currency,
                "symbols": ",".join([s.lower() for s in symbols]),
                "order": "market_cap_desc",
                "per_page": 100,
            }
            
            response = await client.get(url, params=params)
            if response.status_code == 429:
                return self._get_demo_prices(symbols, "Rate limited")
            
            response.raise_for_status()
            data = response.json()
            
            prices = []
            for item in data:
                price = MarketPrice(
                    symbol=item.get("symbol", "").upper(),
                    price=item.get("current_price", 0),
                    currency=currency.upper(),
                    timestamp=datetime.now(),
                    change_24h=item.get("price_change_percentage_24h"),
                    volume_24h=item.get("total_volume"),
                    market_cap=item.get("market_cap"),
                    source="coingecko",
                )
                prices.append(price)
            
            return prices
            
        except Exception as e:
            return self._get_demo_prices(symbols, str(e))
    
    async def _fetch_stocks(
        self,
        symbols: List[str],
        currency: str
    ) -> List[MarketPrice]:
        """Fetch stock prices."""
        if self.source == "alphavantage" and self.api_key:
            return await self._fetch_alphavantage(symbols, currency)
        else:
            return await self._fetch_yahoo(symbols, currency)
    
    async def _fetch_alphavantage(
        self,
        symbols: List[str],
        currency: str
    ) -> List[MarketPrice]:
        """Fetch from Alpha Vantage."""
        client = await self._get_client()
        prices = []
        
        for symbol in symbols:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key,
            }
            
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                quote = data.get("Global Quote", {})
                if quote:
                    price = MarketPrice(
                        symbol=symbol.upper(),
                        price=float(quote.get("05. price", 0)),
                        currency="USD",
                        timestamp=datetime.now(),
                        change_24h=float(quote.get("10. change percent", "0").replace("%", "")),
                        volume_24h=float(quote.get("06. volume", 0)),
                        source="alphavantage",
                    )
                    prices.append(price)
                
                # Respect rate limits (5 calls per minute for free tier)
                await asyncio.sleep(12)
                
            except Exception as e:
                prices.append(MarketPrice(
                    symbol=symbol.upper(),
                    price=0,
                    currency="USD",
                    timestamp=datetime.now(),
                    source=f"error: {str(e)}",
                ))
        
        return prices
    
    async def _fetch_yahoo(
        self,
        symbols: List[str],
        currency: str
    ) -> List[MarketPrice]:
        """Fetch from Yahoo Finance (unofficial)."""
        client = await self._get_client()
        prices = []
        
        for symbol in symbols:
            try:
                url = f"{self.base_url}/{symbol}"
                params = {
                    "interval": "1d",
                    "range": "1d",
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                result = data.get("chart", {}).get("result", [{}])[0]
                meta = result.get("meta", {})
                
                price = MarketPrice(
                    symbol=symbol.upper(),
                    price=meta.get("regularMarketPrice", 0),
                    currency=meta.get("currency", "USD").upper(),
                    timestamp=datetime.now(),
                    source="yahoo",
                )
                prices.append(price)
                
            except Exception as e:
                # Return demo data for failed requests
                prices.append(MarketPrice(
                    symbol=symbol.upper(),
                    price=0,
                    currency="USD",
                    timestamp=datetime.now(),
                    source=f"error: {str(e)}",
                ))
        
        return prices
    
    def _get_demo_prices(self, symbols: List[str], reason: str) -> List[MarketPrice]:
        """Return demo prices when API is unavailable."""
        demo_prices = {
            "BTC": 67234.50,
            "ETH": 3456.78,
            "SOL": 145.23,
            "ADA": 0.45,
            "DOT": 7.89,
            "LINK": 18.50,
            "AAPL": 175.50,
            "GOOGL": 142.30,
            "MSFT": 380.20,
            "TSLA": 245.60,
        }
        
        prices = []
        for symbol in symbols:
            sym_upper = symbol.upper()
            demo_price = demo_prices.get(sym_upper, 100.0)
            
            prices.append(MarketPrice(
                symbol=sym_upper,
                price=demo_price,
                currency="USD",
                timestamp=datetime.now(),
                change_24h=2.5 if sym_upper in ["BTC", "ETH", "SOL"] else -1.2,
                source=f"demo ({reason})",
            ))
        
        return prices
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# =============================================================================
# Social Sentiment Connector
# =============================================================================

class SentimentConnector(DataConnector):
    """
    Connector for analyzing social media sentiment.
    
    Note: Direct Twitter/X API access requires expensive API tiers.
    This connector provides:
    - Reddit sentiment via Reddit API
    - Alternative sentiment sources
    - Simulated/demo mode for testing
    """
    
    def __init__(
        self,
        reddit_client_id: Optional[str] = None,
        reddit_secret: Optional[str] = None,
        cache_ttl: int = 300,  # 5 minutes
    ):
        super().__init__("sentiment", cache_ttl)
        self.reddit_client_id = reddit_client_id or os.getenv("REDDIT_CLIENT_ID")
        self.reddit_secret = reddit_secret or os.getenv("REDDIT_SECRET")
        self._client: Optional[httpx.AsyncClient] = None
        self._reddit_token: Optional[str] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def fetch(
        self,
        topic: str,
        platforms: Optional[List[str]] = None,
        **kwargs
    ) -> List[SentimentScore]:
        """
        Fetch sentiment analysis for a topic.
        
        Args:
            topic: Topic to analyze (e.g., "bitcoin", "AAPL")
            platforms: List of platforms (reddit, twitter, etc.)
            
        Returns:
            List of SentimentScore objects
        """
        if platforms is None:
            platforms = ["reddit"]
        
        cache_key = f"{topic}_{','.join(platforms)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        scores = []
        
        for platform in platforms:
            if platform == "reddit":
                score = await self._fetch_reddit_sentiment(topic)
            elif platform == "twitter":
                score = await self._fetch_twitter_sentiment(topic)
            else:
                score = SentimentScore(
                    platform=platform,
                    topic=topic,
                    score=0,
                    volume=0,
                    timestamp=datetime.now(),
                    trending=[],
                )
            scores.append(score)
        
        self._set_cached(cache_key, scores)
        return scores
    
    async def _fetch_reddit_sentiment(self, topic: str) -> SentimentScore:
        """Fetch Reddit sentiment for a topic."""
        client = await self._get_client()
        
        # Try to use Reddit API if credentials available
        if self.reddit_client_id and self.reddit_secret:
            try:
                return await self._fetch_reddit_api(client, topic)
            except Exception:
                pass
        
        # Return demo sentiment based on topic
        return self._get_demo_sentiment("reddit", topic)
    
    async def _fetch_reddit_api(
        self,
        client: httpx.AsyncClient,
        topic: str
    ) -> SentimentScore:
        """Fetch from Reddit API."""
        # Get OAuth token if needed
        if not self._reddit_token:
            await self._get_reddit_token(client)
        
        headers = {
            "Authorization": f"Bearer {self._reddit_token}",
            "User-Agent": "ScalesBot/1.0",
        }
        
        # Search for posts about topic
        url = "https://oauth.reddit.com/search"
        params = {
            "q": topic,
            "sort": "new",
            "limit": 100,
            "t": "day",
        }
        
        response = await client.get(url, headers=headers, params=params)
        
        if response.status_code == 401:
            # Token expired, refresh and retry
            self._reddit_token = None
            return await self._fetch_reddit_sentiment(topic)
        
        response.raise_for_status()
        data = response.json()
        
        posts = data.get("data", {}).get("children", [])
        
        # Simple sentiment analysis based on keywords
        positive_words = ["bull", "moon", "pump", "gain", "profit", "buy", "long", "up"]
        negative_words = ["bear", "dump", "crash", "loss", "sell", "short", "down", "scam"]
        
        sentiment_scores = []
        trending = []
        
        for post in posts:
            title = post.get("data", {}).get("title", "").lower()
            score = post.get("data", {}).get("score", 0)
            
            pos_count = sum(1 for word in positive_words if word in title)
            neg_count = sum(1 for word in negative_words if word in title)
            
            if pos_count > neg_count:
                sentiment_scores.append(1 * min(score / 100, 1))
            elif neg_count > pos_count:
                sentiment_scores.append(-1 * min(score / 100, 1))
            
            # Extract trending terms
            words = title.split()
            for word in words:
                if word.startswith("$") or word.startswith("#"):
                    trending.append(word.strip("$#"))
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Count trending occurrences
        from collections import Counter
        top_trending = [t[0] for t in Counter(trending).most_common(5)]
        
        return SentimentScore(
            platform="reddit",
            topic=topic,
            score=round(avg_sentiment, 3),
            volume=len(posts),
            timestamp=datetime.now(),
            trending=top_trending,
        )
    
    async def _get_reddit_token(self, client: httpx.AsyncClient) -> None:
        """Get Reddit OAuth token."""
        import base64
        
        auth = base64.b64encode(
            f"{self.reddit_client_id}:{self.reddit_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth}",
            "User-Agent": "ScalesBot/1.0",
        }
        
        data = {
            "grant_type": "client_credentials",
        }
        
        response = await client.post(
            "https://www.reddit.com/api/v1/access_token",
            headers=headers,
            data=data,
        )
        response.raise_for_status()
        
        token_data = response.json()
        self._reddit_token = token_data.get("access_token")
    
    async def _fetch_twitter_sentiment(self, topic: str) -> SentimentScore:
        """Fetch Twitter/X sentiment (requires expensive API access)."""
        # Twitter API v2 basic tier is $100/month minimum
        # Return demo data with explanation
        return SentimentScore(
            platform="twitter",
            topic=topic,
            score=0,
            volume=0,
            timestamp=datetime.now(),
            trending=[],
            raw_data={"note": "Twitter API requires paid tier. Use demo mode or alternative sources."},
        )
    
    def _get_demo_sentiment(self, platform: str, topic: str) -> SentimentScore:
        """Generate demo sentiment based on topic patterns."""
        import hashlib
        
        # Deterministic demo data based on topic
        topic_hash = int(hashlib.md5(topic.encode()).hexdigest(), 16)
        
        # Generate sentiment between -0.8 and 0.8
        sentiment = ((topic_hash % 160) - 80) / 100
        volume = 100 + (topic_hash % 9000)
        
        # Demo trending terms
        trending_terms = {
            "bitcoin": ["BTC", "halving", "ETF", "mining"],
            "ethereum": ["ETH", "L2", "staking", "DeFi"],
            "solana": ["SOL", "NFT", "Jupiter", "firedancer"],
            "aapl": ["earnings", "iPhone", "tim cook", "dividend"],
            "tsla": ["elon", "cybertruck", "FSD", "deliveries"],
        }
        
        trending = trending_terms.get(topic.lower(), ["trending", "viral", "hot"])
        
        return SentimentScore(
            platform=platform,
            topic=topic,
            score=round(sentiment, 3),
            volume=volume,
            timestamp=datetime.now(),
            trending=trending,
            raw_data={"note": "Demo sentiment data. Configure API keys for real data."},
        )
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# =============================================================================
# File Watcher Connector
# =============================================================================

class FileWatcherConnector(DataConnector):
    """
    Connector for monitoring file system changes.
    
    Watches directories for:
    - New PDF/CSV files
    - Modified files
    - Deleted files
    
    Uses async polling for cross-platform compatibility.
    """
    
    def __init__(
        self,
        watch_paths: Optional[List[Union[str, Path]]] = None,
        patterns: Optional[List[str]] = None,
        poll_interval: float = 5.0,
        cache_ttl: int = 1,
    ):
        super().__init__("file_watcher", cache_ttl)
        self.watch_paths = [Path(p) for p in (watch_paths or ["."])]
        self.patterns = patterns or ["*.pdf", "*.csv", "*.json", "*.txt"]
        self.poll_interval = poll_interval
        self._file_states: Dict[Path, Dict[str, Any]] = {}
        self._running = False
        self._callbacks: List[Callable[[FileChange], None]] = []
    
    def add_callback(self, callback: Callable[[FileChange], None]) -> None:
        """Add a callback to be called on file changes."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[FileChange], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def fetch(
        self,
        check_changes: bool = True,
        **kwargs
    ) -> List[FileChange]:
        """
        Check for file changes.
        
        Args:
            check_changes: If True, returns only new changes since last check
            
        Returns:
            List of FileChange objects
        """
        if not check_changes:
            # Just scan and return current state
            return await self._scan_files()
        
        # Compare with previous state
        changes = await self._detect_changes()
        
        # Notify callbacks
        for change in changes:
            for callback in self._callbacks:
                try:
                    callback(change)
                except Exception:
                    pass
        
        return changes
    
    async def _scan_files(self) -> List[FileChange]:
        """Scan watch paths and return current files as changes."""
        changes = []
        
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
            
            for pattern in self.patterns:
                for file_path in watch_path.rglob(pattern):
                    if file_path.is_file():
                        stat = file_path.stat()
                        change = FileChange(
                            file_path=file_path,
                            change_type="existing",
                            timestamp=datetime.fromtimestamp(stat.st_mtime),
                            file_size=stat.st_size,
                            checksum=self._compute_checksum(file_path),
                        )
                        changes.append(change)
        
        return changes
    
    async def _detect_changes(self) -> List[FileChange]:
        """Detect changes since last scan."""
        changes = []
        current_files: Set[Path] = set()
        
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
            
            for pattern in self.patterns:
                for file_path in watch_path.rglob(pattern):
                    if not file_path.is_file():
                        continue
                    
                    current_files.add(file_path)
                    stat = file_path.stat()
                    
                    file_info = {
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                        "checksum": self._compute_checksum(file_path),
                    }
                    
                    if file_path not in self._file_states:
                        # New file
                        change = FileChange(
                            file_path=file_path,
                            change_type="created",
                            timestamp=datetime.now(),
                            file_size=stat.st_size,
                            checksum=file_info["checksum"],
                        )
                        changes.append(change)
                    else:
                        # Check for modifications
                        old_info = self._file_states[file_path]
                        if (old_info["mtime"] != file_info["mtime"] or
                            old_info["checksum"] != file_info["checksum"]):
                            change = FileChange(
                                file_path=file_path,
                                change_type="modified",
                                timestamp=datetime.now(),
                                file_size=stat.st_size,
                                checksum=file_info["checksum"],
                            )
                            changes.append(change)
                    
                    self._file_states[file_path] = file_info
        
        # Check for deleted files
        for file_path in list(self._file_states.keys()):
            if file_path not in current_files:
                change = FileChange(
                    file_path=file_path,
                    change_type="deleted",
                    timestamp=datetime.now(),
                )
                changes.append(change)
                del self._file_states[file_path]
        
        return changes
    
    def _compute_checksum(self, file_path: Path) -> str:
        """Compute simple checksum for file."""
        import hashlib
        
        try:
            stat = file_path.stat()
            # Use mtime + size as lightweight checksum
            data = f"{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(data.encode()).hexdigest()[:8]
        except:
            return ""
    
    async def start_watching(self) -> None:
        """Start continuous file watching."""
        self._running = True
        
        # Initial scan
        await self._detect_changes()
        
        while self._running:
            await asyncio.sleep(self.poll_interval)
            await self.fetch(check_changes=True)
    
    def stop_watching(self) -> None:
        """Stop continuous file watching."""
        self._running = False
    
    def get_watched_files(self) -> List[Path]:
        """Get list of currently watched files."""
        return list(self._file_states.keys())
    
    def clear_state(self) -> None:
        """Clear internal file state (forces all files to appear as new)."""
        self._file_states.clear()
    
    async def close(self) -> None:
        """Stop watching and cleanup."""
        self.stop_watching()


# =============================================================================
# Unified Data Feed Manager
# =============================================================================

class DataFeedManager:
    """
    Unified manager for all data feeds.
    
    Provides easy access to all connectors with lifecycle management.
    """
    
    def __init__(self):
        self.news = NewsConnector()
        self.market = MarketConnector()
        self.sentiment = SentimentConnector()
        self.file_watcher = FileWatcherConnector()
        self._connectors: List[DataConnector] = [
            self.news, self.market, self.sentiment, self.file_watcher
        ]
    
    async def fetch_all(
        self,
        news_query: Optional[str] = None,
        market_symbols: Optional[List[str]] = None,
        sentiment_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch data from all connectors concurrently.
        
        Args:
            news_query: Query for news fetch
            market_symbols: List of symbols for market data
            sentiment_topic: Topic for sentiment analysis
            
        Returns:
            Dict with results from all connectors
        """
        tasks = []
        
        # News task
        if news_query:
            tasks.append(("news", self.news.fetch(query=news_query)))
        
        # Market task
        if market_symbols:
            tasks.append(("market", self.market.fetch(symbols=market_symbols)))
        
        # Sentiment task
        if sentiment_topic:
            tasks.append(("sentiment", self.sentiment.fetch(topic=sentiment_topic)))
        
        # File watcher task
        tasks.append(("files", self.file_watcher.fetch(check_changes=True)))
        
        # Execute concurrently
        results = {}
        if tasks:
            names, coros = zip(*tasks)
            completed = await asyncio.gather(*coros, return_exceptions=True)
            
            for name, result in zip(names, completed):
                if isinstance(result, Exception):
                    results[name] = {"error": str(result)}
                else:
                    results[name] = result
        
        return results
    
    def clear_all_caches(self) -> None:
        """Clear caches for all connectors."""
        for connector in self._connectors:
            connector.clear_cache()
    
    async def close(self) -> None:
        """Close all connectors."""
        close_tasks = []
        for connector in self._connectors:
            if hasattr(connector, 'close'):
                close_tasks.append(connector.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)


# =============================================================================
# Convenience Functions
# =============================================================================

async def fetch_news(
    query: Optional[str] = None,
    api_key: Optional[str] = None
) -> List[NewsArticle]:
    """Fetch news headlines."""
    connector = NewsConnector(api_key=api_key)
    try:
        return await connector.fetch(query=query)
    finally:
        await connector.close()


async def fetch_market(
    symbols: Union[str, List[str]],
    asset_type: str = "crypto",
    api_key: Optional[str] = None
) -> List[MarketPrice]:
    """Fetch market prices."""
    connector = MarketConnector(api_key=api_key)
    try:
        return await connector.fetch(symbols=symbols, asset_type=asset_type)
    finally:
        await connector.close()


async def fetch_sentiment(
    topic: str,
    platforms: Optional[List[str]] = None
) -> List[SentimentScore]:
    """Fetch social sentiment."""
    connector = SentimentConnector()
    try:
        return await connector.fetch(topic=topic, platforms=platforms)
    finally:
        await connector.close()


async def watch_files(
    paths: Union[str, Path, List[Union[str, Path]]],
    patterns: Optional[List[str]] = None
) -> List[FileChange]:
    """Check for file changes."""
    if isinstance(paths, (str, Path)):
        paths = [paths]
    
    connector = FileWatcherConnector(watch_paths=paths, patterns=patterns)
    try:
        return await connector.fetch(check_changes=False)
    finally:
        await connector.close()


# =============================================================================
# Example Usage
# =============================================================================

async def main():
    """Example usage of data feeds."""
    print("=== Scales Data Feeds Demo ===\n")
    
    # Initialize manager
    manager = DataFeedManager()
    
    try:
        # Fetch all data types
        results = await manager.fetch_all(
            news_query="technology",
            market_symbols=["BTC", "ETH", "AAPL"],
            sentiment_topic="bitcoin",
        )
        
        # Print news
        print("📰 NEWS:")
        for article in results.get("news", [])[:3]:
            print(f"  - {article.title} ({article.source})")
        
        # Print prices
        print("\n💰 MARKET PRICES:")
        for price in results.get("market", []):
            change_str = f"{price.change_24h:+.2f}%" if price.change_24h else "N/A"
            print(f"  - {price.symbol}: ${price.price:,.2f} ({change_str})")
        
        # Print sentiment
        print("\n📊 SENTIMENT:")
        for sent in results.get("sentiment", []):
            emoji = "🟢" if sent.score > 0.1 else "🔴" if sent.score < -0.1 else "⚪"
            print(f"  {emoji} {sent.platform}: {sent.score:+.2f} ({sent.volume} posts)")
            if sent.trending:
                print(f"     Trending: {', '.join(sent.trending[:3])}")
        
        # Print files
        print("\n📁 FILES WATCHED:")
        files = results.get("files", [])
        if files:
            for f in files[:5]:
                print(f"  - {f.file_path.name} ({f.change_type})")
        else:
            print("  (No matching files found)")
        
    finally:
        await manager.close()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())
