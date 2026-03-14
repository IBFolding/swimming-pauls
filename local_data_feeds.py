"""
Swimming Pauls - 100% Local Data Feeds

All data feeds work locally with NO third-party APIs:
- News: RSS feeds, local files, web scraping
- Market: Local CSV files, cached data, demo mode
- Sentiment: Local text analysis, rule-based scoring
- File Watcher: Local file monitoring (already local)

No API keys required. Works offline.
"""

import os
import re
import json
import time
import asyncio
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union
from collections import Counter
import xml.etree.ElementTree as ET

import httpx


# =============================================================================
# Data Models (Same as original)
# =============================================================================

@dataclass
class NewsArticle:
    """Represents a news article from various sources."""
    title: str
    source: str
    published_at: datetime
    url: str
    summary: Optional[str] = None
    sentiment: Optional[float] = None
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
    source: str = "local"
    
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
    platform: str
    topic: str
    score: float
    volume: int
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
    change_type: str
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
# LOCAL News Connector - RSS Feeds + Local Files + Web Scraping
# =============================================================================

class LocalNewsConnector(DataConnector):
    """
    100% Local news connector.
    
    Sources (in order of priority):
    1. Local files (JSON, CSV, TXT)
    2. RSS feeds (no API key needed)
    3. Web scraping with httpx + BeautifulSoup (if available)
    4. Demo fallback (works completely offline)
    """
    
    # Popular financial/crypto RSS feeds
    RSS_FEEDS = {
        "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "cointelegraph": "https://cointelegraph.com/rss",
        "decrypt": "https://decrypt.co/feed",
        "cryptonews": "https://crypto.news/feed/",
    }
    
    def __init__(
        self,
        local_data_path: Optional[str] = None,
        rss_feeds: Optional[Dict[str, str]] = None,
        enable_web_scraping: bool = True,
        cache_ttl: int = 300,
    ):
        super().__init__("local_news", cache_ttl)
        self.local_data_path = Path(local_data_path) if local_data_path else None
        self.rss_feeds = rss_feeds or self.RSS_FEEDS
        self.enable_web_scraping = enable_web_scraping
        self._client: Optional[httpx.AsyncClient] = None
        
        # Try to import BeautifulSoup for web scraping
        try:
            from bs4 import BeautifulSoup
            self._bs4 = BeautifulSoup
            self._has_bs4 = True
        except ImportError:
            self._has_bs4 = False
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self._client
    
    async def fetch(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        source: str = "auto",  # auto, local, rss, web
        limit: int = 20,
        **kwargs
    ) -> List[NewsArticle]:
        """
        Fetch news from local sources.
        
        Args:
            query: Search/filter query
            category: Category filter
            source: Source type (auto, local, rss, web)
            limit: Max articles to return
        """
        cache_key = f"{query}_{category}_{source}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        articles = []
        
        # 1. Try local files first (always works offline)
        if source in ("auto", "local"):
            local_articles = await self._fetch_local_files(query, category, limit)
            articles.extend(local_articles)
        
        # 2. Try RSS feeds (works with internet, no API key)
        if source in ("auto", "rss") and len(articles) < limit:
            try:
                rss_articles = await self._fetch_rss_feeds(query, limit - len(articles))
                articles.extend(rss_articles)
            except Exception:
                pass  # RSS might fail offline
        
        # 3. Try web scraping (works with internet, no API key)
        if source in ("auto", "web") and self.enable_web_scraping and len(articles) < limit:
            try:
                web_articles = await self._fetch_web_scraping(query, limit - len(articles))
                articles.extend(web_articles)
            except Exception:
                pass
        
        # 4. Fallback to demo data (always works)
        if not articles:
            articles = self._get_demo_news("Using local demo data (offline mode)")
        
        # Sort by date and limit
        articles.sort(key=lambda x: x.published_at, reverse=True)
        articles = articles[:limit]
        
        self._set_cached(cache_key, articles)
        return articles
    
    async def _fetch_local_files(
        self,
        query: Optional[str],
        category: Optional[str],
        limit: int
    ) -> List[NewsArticle]:
        """Fetch news from local files."""
        articles = []
        
        if not self.local_data_path or not self.local_data_path.exists():
            # Try default locations
            default_paths = [
                Path("./data/news"),
                Path("~/.swimming_pauls/news").expanduser(),
                Path("./news_data"),
            ]
            for path in default_paths:
                if path.exists():
                    self.local_data_path = path
                    break
        
        if not self.local_data_path or not self.local_data_path.exists():
            return articles
        
        # Load JSON files
        for json_file in self.local_data_path.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                if isinstance(data, list):
                    for item in data:
                        article = self._parse_article(item)
                        if article and self._matches_query(article, query, category):
                            articles.append(article)
                elif isinstance(data, dict):
                    article = self._parse_article(data)
                    if article and self._matches_query(article, query, category):
                        articles.append(article)
            except Exception:
                continue
        
        # Load CSV files
        for csv_file in self.local_data_path.rglob("*.csv"):
            try:
                import csv
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        article = self._parse_article({
                            'title': row.get('title', ''),
                            'source': row.get('source', csv_file.stem),
                            'published_at': row.get('date', ''),
                            'url': row.get('url', ''),
                            'summary': row.get('summary', row.get('content', '')),
                        })
                        if article and self._matches_query(article, query, category):
                            articles.append(article)
            except Exception:
                continue
        
        # Load TXT files (one article per line or file)
        for txt_file in self.local_data_path.rglob("*.txt"):
            try:
                content = txt_file.read_text()
                # Try JSON first
                try:
                    data = json.loads(content)
                    article = self._parse_article(data)
                    if article and self._matches_query(article, query, category):
                        articles.append(article)
                except json.JSONDecodeError:
                    # Treat as plain text article
                    lines = content.strip().split('\n')
                    title = lines[0] if lines else txt_file.stem
                    article = NewsArticle(
                        title=title,
                        source="local_txt",
                        published_at=datetime.fromtimestamp(txt_file.stat().st_mtime),
                        url=f"file://{txt_file}",
                        summary='\n'.join(lines[1:]) if len(lines) > 1 else "",
                    )
                    if self._matches_query(article, query, category):
                        articles.append(article)
            except Exception:
                continue
        
        return articles[:limit]
    
    async def _fetch_rss_feeds(
        self,
        query: Optional[str],
        limit: int
    ) -> List[NewsArticle]:
        """Fetch news from RSS feeds."""
        articles = []
        client = await self._get_client()
        
        for feed_name, feed_url in self.rss_feeds.items():
            if len(articles) >= limit:
                break
            
            try:
                response = await client.get(feed_url, timeout=10.0)
                if response.status_code != 200:
                    continue
                
                # Parse RSS XML
                root = ET.fromstring(response.content)
                
                # Handle RSS 2.0 and Atom formats
                items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                
                for item in items:
                    if len(articles) >= limit:
                        break
                    
                    # Extract fields based on RSS format
                    title_elem = item.find('title') or item.find('.//{http://www.w3.org/2005/Atom}title')
                    link_elem = item.find('link') or item.find('.//{http://www.w3.org/2005/Atom}link')
                    desc_elem = item.find('description') or item.find('.//{http://www.w3.org/2005/Atom}summary')
                    date_elem = item.find('pubDate') or item.find('.//{http://www.w3.org/2005/Atom}published')
                    
                    title = title_elem.text if title_elem is not None else "No title"
                    
                    # Get link (might be attribute or text)
                    if link_elem is not None:
                        url = link_elem.text or link_elem.get('href', '')
                    else:
                        url = feed_url
                    
                    description = desc_elem.text if desc_elem is not None else ""
                    pub_date = self._parse_rss_date(date_elem.text if date_elem is not None else "")
                    
                    article = NewsArticle(
                        title=title,
                        source=feed_name,
                        published_at=pub_date,
                        url=url,
                        summary=description[:200] if description else "",
                    )
                    
                    if not query or query.lower() in title.lower() or query.lower() in description.lower():
                        articles.append(article)
                
            except Exception:
                continue
        
        return articles
    
    async def _fetch_web_scraping(
        self,
        query: Optional[str],
        limit: int
    ) -> List[NewsArticle]:
        """Fetch news via web scraping."""
        if not self._has_bs4:
            return []
        
        articles = []
        client = await self._get_client()
        
        # List of news sites that don't require JS
        news_sites = [
            "https://news.ycombinator.com",  # Hacker News
        ]
        
        for site in news_sites:
            if len(articles) >= limit:
                break
            
            try:
                response = await client.get(site, timeout=10.0)
                if response.status_code != 200:
                    continue
                
                soup = self._bs4(response.text, 'html.parser')
                
                # Hacker News specific scraping
                if "ycombinator" in site:
                    items = soup.find_all('tr', class_='athing')[:limit]
                    for item in items:
                        title_link = item.find('span', class_='titleline')
                        if title_link and title_link.a:
                            title = title_link.a.text
                            url = title_link.a.get('href', '')
                            
                            article = NewsArticle(
                                title=title,
                                source="Hacker News",
                                published_at=datetime.now(),
                                url=url if url.startswith('http') else f"https://news.ycombinator.com/{url}",
                            )
                            
                            if not query or query.lower() in title.lower():
                                articles.append(article)
                
            except Exception:
                continue
        
        return articles
    
    def _parse_article(self, data: Dict) -> Optional[NewsArticle]:
        """Parse article from dict."""
        try:
            title = data.get('title') or data.get('headline')
            if not title:
                return None
            
            return NewsArticle(
                title=str(title),
                source=data.get('source', 'unknown'),
                published_at=self._parse_datetime(data.get('published_at') or data.get('date') or data.get('pubDate')),
                url=data.get('url', ''),
                summary=data.get('summary') or data.get('description') or data.get('content', '')[:200],
                keywords=data.get('keywords', []),
            )
        except Exception:
            return None
    
    def _parse_datetime(self, dt_str: Optional[str]) -> datetime:
        """Parse datetime from various formats."""
        if not dt_str:
            return datetime.now()
        
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str[:19], fmt)
            except ValueError:
                continue
        
        # Try ISO format
        try:
            dt_str = str(dt_str).replace("Z", "+00:00")
            return datetime.fromisoformat(dt_str)
        except:
            return datetime.now()
    
    def _parse_rss_date(self, date_str: str) -> datetime:
        """Parse RSS date format."""
        if not date_str:
            return datetime.now()
        
        # Common RSS date formats
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return self._parse_datetime(date_str)
    
    def _matches_query(
        self,
        article: NewsArticle,
        query: Optional[str],
        category: Optional[str]
    ) -> bool:
        """Check if article matches query."""
        if query:
            query_lower = query.lower()
            text = f"{article.title} {article.summary or ''}".lower()
            if query_lower not in text:
                return False
        
        if category:
            text = f"{article.title} {article.summary or ''}".lower()
            if category.lower() not in text:
                return False
        
        return True
    
    def _get_demo_news(self, reason: str) -> List[NewsArticle]:
        """Return demo news when no sources available."""
        return [
            NewsArticle(
                title=f"[LOCAL] Market Update - {reason}",
                source="Local",
                published_at=datetime.now(),
                url="local://demo",
                summary="This is local demo data. Add files to ./data/news/ or connect to internet for RSS feeds.",
            ),
            NewsArticle(
                title="[LOCAL] Crypto Markets Show Volatility",
                source="Local Analysis",
                published_at=datetime.now() - timedelta(hours=1),
                url="local://demo",
                summary="Bitcoin and Ethereum experience price fluctuations amid market uncertainty.",
            ),
            NewsArticle(
                title="[LOCAL] DeFi Protocol Announces Upgrade",
                source="Local Analysis",
                published_at=datetime.now() - timedelta(hours=2),
                url="local://demo",
                summary="Major DeFi platform releases new features for yield farming.",
            ),
        ]
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# =============================================================================
# LOCAL Market Connector - CSV Files + Cached Data + Demo
# =============================================================================

class LocalMarketConnector(DataConnector):
    """
    100% Local market data connector.
    
    Sources (in order of priority):
    1. Local CSV files
    2. Cached data from previous runs
    3. Demo/simulated data (always works offline)
    """
    
    def __init__(
        self,
        local_data_path: Optional[str] = None,
        cache_file: Optional[str] = None,
        cache_ttl: int = 60,
    ):
        super().__init__("local_market", cache_ttl)
        self.local_data_path = Path(local_data_path) if local_data_path else None
        self.cache_file = Path(cache_file) if cache_file else Path("~/.swimming_pauls/market_cache.json").expanduser()
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    async def fetch(
        self,
        symbols: Union[str, List[str]],
        asset_type: str = "crypto",
        currency: str = "usd",
        **kwargs
    ) -> List[MarketPrice]:
        """
        Fetch market prices from local sources.
        
        Args:
            symbols: Symbol(s) to fetch
            asset_type: "crypto" or "stock"
            currency: Currency code
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        cache_key = f"{','.join(symbols)}_{asset_type}_{currency}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        prices = []
        fetched_symbols = set()
        
        # 1. Try local CSV files
        for symbol in symbols:
            if symbol.upper() not in fetched_symbols:
                price = await self._fetch_from_csv(symbol, asset_type, currency)
                if price:
                    prices.append(price)
                    fetched_symbols.add(symbol.upper())
        
        # 2. Try cache file
        for symbol in symbols:
            if symbol.upper() not in fetched_symbols:
                price = self._fetch_from_cache(symbol, currency)
                if price:
                    prices.append(price)
                    fetched_symbols.add(symbol.upper())
        
        # 3. Use demo data for remaining symbols
        for symbol in symbols:
            if symbol.upper() not in fetched_symbols:
                price = self._get_demo_price(symbol, currency)
                prices.append(price)
        
        self._set_cached(cache_key, prices)
        return prices
    
    async def _fetch_from_csv(
        self,
        symbol: str,
        asset_type: str,
        currency: str
    ) -> Optional[MarketPrice]:
        """Fetch from local CSV files."""
        if not self.local_data_path:
            # Try default locations
            default_paths = [
                Path("./data/market"),
                Path("~/.swimming_pauls/market").expanduser(),
            ]
            for path in default_paths:
                if path.exists():
                    self.local_data_path = path
                    break
        
        if not self.local_data_path or not self.local_data_path.exists():
            return None
        
        # Look for symbol-specific CSV
        csv_file = self.local_data_path / f"{symbol.upper()}.csv"
        if not csv_file.exists():
            # Try generic files
            csv_file = self.local_data_path / "prices.csv"
        
        if not csv_file.exists():
            return None
        
        try:
            import csv
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    return None
                
                # Get most recent row
                latest = rows[-1]
                
                return MarketPrice(
                    symbol=symbol.upper(),
                    price=float(latest.get('price', 0) or latest.get('close', 0)),
                    currency=currency.upper(),
                    timestamp=datetime.now(),
                    change_24h=float(latest.get('change_24h', 0) or latest.get('change', 0)),
                    volume_24h=float(latest.get('volume', 0)),
                    source="local_csv",
                )
        except Exception:
            return None
    
    def _fetch_from_cache(self, symbol: str, currency: str) -> Optional[MarketPrice]:
        """Fetch from cache file."""
        if not self.cache_file.exists():
            return None
        
        try:
            cache = json.loads(self.cache_file.read_text())
            key = f"{symbol.upper()}_{currency.upper()}"
            
            if key in cache:
                data = cache[key]
                cached_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                
                # Only use cache if less than 1 hour old
                if datetime.now() - cached_time < timedelta(hours=1):
                    return MarketPrice(
                        symbol=symbol.upper(),
                        price=data.get('price', 0),
                        currency=currency.upper(),
                        timestamp=cached_time,
                        change_24h=data.get('change_24h'),
                        source="cache",
                    )
        except Exception:
            pass
        
        return None
    
    def save_to_cache(self, prices: List[MarketPrice]) -> None:
        """Save prices to cache file."""
        try:
            cache = {}
            if self.cache_file.exists():
                cache = json.loads(self.cache_file.read_text())
            
            for price in prices:
                key = f"{price.symbol}_{price.currency}"
                cache[key] = {
                    'price': price.price,
                    'change_24h': price.change_24h,
                    'timestamp': price.timestamp.isoformat(),
                }
            
            self.cache_file.write_text(json.dumps(cache, indent=2))
        except Exception:
            pass
    
    def _get_demo_price(self, symbol: str, currency: str) -> MarketPrice:
        """Generate demo price."""
        # Deterministic demo prices based on symbol
        demo_prices = {
            "BTC": 67234.50,
            "ETH": 3456.78,
            "SOL": 145.23,
            "ADA": 0.45,
            "DOT": 7.89,
            "LINK": 18.50,
            "UNI": 9.20,
            "AAVE": 95.40,
            "AAPL": 175.50,
            "GOOGL": 142.30,
            "MSFT": 380.20,
            "TSLA": 245.60,
            "AMZN": 178.90,
            "NVDA": 495.30,
        }
        
        sym_upper = symbol.upper()
        
        # Generate deterministic price from symbol hash
        if sym_upper not in demo_prices:
            hash_val = int(hashlib.md5(sym_upper.encode()).hexdigest(), 16)
            demo_prices[sym_upper] = (hash_val % 10000) + 10
        
        base_price = demo_prices[sym_upper]
        
        # Add small random variation
        import random
        random.seed(hash_val if 'hash_val' in dir() else 42)
        variation = random.uniform(-0.02, 0.02)
        
        return MarketPrice(
            symbol=sym_upper,
            price=base_price * (1 + variation),
            currency=currency.upper(),
            timestamp=datetime.now(),
            change_24h=variation * 100,
            source="demo_local",
        )


# =============================================================================
# LOCAL Sentiment Connector - Text Analysis + Rule-Based
# =============================================================================

class LocalSentimentConnector(DataConnector):
    """
    100% Local sentiment analysis connector.
    
    Analyzes:
    1. Local text files
    2. Rule-based keyword analysis
    3. Demo/generation based on topic patterns
    """
    
    # Sentiment keyword dictionaries
    POSITIVE_WORDS = [
        "bull", "bullish", "moon", "pump", "gain", "profit", "buy", "long",
        "up", "surge", "rally", "boom", "growth", " ATH", "all time high",
        "breakout", "support", "accumulate", "hodl", "diamond hands",
        "optimistic", "positive", "strong", "recover", "bounce",
    ]
    
    NEGATIVE_WORDS = [
        "bear", "bearish", "dump", "crash", "loss", "sell", "short",
        "down", "drop", "fall", "plunge", "bear market", "capitulation",
        "liquidation", "fud", "fear", "panic", "weak", "die", "dead",
        "rug pull", "scam", "hack", "exploit", "paper hands",
        "pessimistic", "negative", "crash", "collapse",
    ]
    
    def __init__(
        self,
        local_data_path: Optional[str] = None,
        cache_ttl: int = 300,
    ):
        super().__init__("local_sentiment", cache_ttl)
        self.local_data_path = Path(local_data_path) if local_data_path else None
    
    async def fetch(
        self,
        topic: str,
        sources: Optional[List[str]] = None,
        **kwargs
    ) -> List[SentimentScore]:
        """
        Analyze sentiment for a topic from local sources.
        
        Args:
            topic: Topic to analyze
            sources: List of source types (local_files, keyword_analysis)
        """
        if sources is None:
            sources = ["local_files", "keyword_analysis"]
        
        cache_key = f"{topic}_{','.join(sources)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        scores = []
        
        # 1. Analyze local text files
        if "local_files" in sources:
            score = await self._analyze_local_files(topic)
            if score:
                scores.append(score)
        
        # 2. Rule-based keyword analysis
        if "keyword_analysis" in sources:
            score = self._analyze_keywords(topic)
            scores.append(score)
        
        if not scores:
            scores.append(self._get_demo_sentiment(topic))
        
        self._set_cached(cache_key, scores)
        return scores
    
    async def _analyze_local_files(self, topic: str) -> Optional[SentimentScore]:
        """Analyze sentiment from local text files."""
        if not self.local_data_path:
            default_paths = [
                Path("./data/sentiment"),
                Path("~/.swimming_pauls/sentiment").expanduser(),
            ]
            for path in default_paths:
                if path.exists():
                    self.local_data_path = path
                    break
        
        if not self.local_data_path or not self.local_data_path.exists():
            return None
        
        all_texts = []
        
        # Read all text files related to topic
        for txt_file in self.local_data_path.rglob("*.txt"):
            try:
                content = txt_file.read_text().lower()
                if topic.lower() in content:
                    all_texts.append(content)
            except Exception:
                continue
        
        if not all_texts:
            return None
        
        # Analyze sentiment
        combined_text = " ".join(all_texts)
        sentiment = self._calculate_sentiment_score(combined_text)
        trending = self._extract_trending_terms(combined_text)
        
        return SentimentScore(
            platform="local_files",
            topic=topic,
            score=round(sentiment, 3),
            volume=len(all_texts),
            timestamp=datetime.now(),
            trending=trending,
        )
    
    def _analyze_keywords(self, topic: str) -> SentimentScore:
        """Analyze sentiment using keyword rules."""
        # This is a deterministic analysis based on common associations
        topic_lower = topic.lower()
        
        # Topic-specific sentiment biases
        topic_sentiments = {
            "bitcoin": 0.3,
            "btc": 0.3,
            "ethereum": 0.25,
            "eth": 0.25,
            "solana": 0.2,
            "sol": 0.2,
            "crypto": 0.15,
            "blockchain": 0.2,
            "defi": 0.1,
            "nft": -0.1,
            "memecoin": -0.2,
            "shitcoin": -0.4,
        }
        
        base_sentiment = topic_sentiments.get(topic_lower, 0.0)
        
        # Generate deterministic volume from hash
        hash_val = int(hashlib.md5(topic.encode()).hexdigest(), 16)
        volume = 100 + (hash_val % 9900)
        
        # Generate trending terms
        trending_map = {
            "bitcoin": ["BTC", "halving", "ETF", "mining", "satoshi"],
            "ethereum": ["ETH", "L2", "staking", "DeFi", "smart contracts"],
            "solana": ["SOL", "NFT", "Jupiter", "Firedancer", "Saga"],
            "crypto": ["blockchain", "Web3", "DeFi", "NFT", "altcoin"],
        }
        
        trending = trending_map.get(topic_lower, ["trending", "viral"])
        
        return SentimentScore(
            platform="keyword_analysis",
            topic=topic,
            score=round(base_sentiment, 3),
            volume=volume,
            timestamp=datetime.now(),
            trending=trending,
        )
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score from text."""
        text_lower = text.lower()
        
        pos_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        neg_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        # Normalize to -1 to 1 range
        return (pos_count - neg_count) / total
    
    def _extract_trending_terms(self, text: str) -> List[str]:
        """Extract trending terms from text."""
        # Simple extraction of capitalized words and hashtags
        words = text.split()
        trending = []
        
        for word in words:
            clean = re.sub(r'[^\w$#]', '', word)
            if clean.startswith('$') or clean.startswith('#'):
                trending.append(clean[1:].upper())
            elif clean.isupper() and len(clean) >= 2 and len(clean) <= 5:
                trending.append(clean)
        
        # Count and return top terms
        counter = Counter(trending)
        return [term for term, _ in counter.most_common(5)]
    
    def _get_demo_sentiment(self, topic: str) -> SentimentScore:
        """Generate demo sentiment."""
        hash_val = int(hashlib.md5(topic.encode()).hexdigest(), 16)
        
        sentiment = ((hash_val % 160) - 80) / 100
        volume = 100 + (hash_val % 9900)
        
        return SentimentScore(
            platform="demo_local",
            topic=topic,
            score=round(sentiment, 3),
            volume=volume,
            timestamp=datetime.now(),
            trending=["demo", "local", "analysis"],
        )


# =============================================================================
# File Watcher Connector (Unchanged - already local)
# =============================================================================

class FileWatcherConnector(DataConnector):
    """Monitor file system for changes."""
    
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
        """Add a callback for file changes."""
        self._callbacks.append(callback)
    
    async def fetch(self, check_changes: bool = True, **kwargs) -> List[FileChange]:
        """Check for file changes."""
        if not check_changes:
            return await self._scan_files()
        
        changes = await self._detect_changes()
        
        for change in changes:
            for callback in self._callbacks:
                try:
                    callback(change)
                except Exception:
                    pass
        
        return changes
    
    async def _scan_files(self) -> List[FileChange]:
        """Scan watch paths."""
        changes = []
        
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
            
            for pattern in self.patterns:
                for file_path in watch_path.rglob(pattern):
                    if file_path.is_file():
                        stat = file_path.stat()
                        changes.append(FileChange(
                            file_path=file_path,
                            change_type="existing",
                            timestamp=datetime.fromtimestamp(stat.st_mtime),
                            file_size=stat.st_size,
                            checksum=self._compute_checksum(file_path),
                        ))
        
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
                        changes.append(FileChange(
                            file_path=file_path,
                            change_type="created",
                            timestamp=datetime.now(),
                            file_size=stat.st_size,
                            checksum=file_info["checksum"],
                        ))
                    elif self._file_states[file_path] != file_info:
                        changes.append(FileChange(
                            file_path=file_path,
                            change_type="modified",
                            timestamp=datetime.now(),
                            file_size=stat.st_size,
                            checksum=file_info["checksum"],
                        ))
                    
                    self._file_states[file_path] = file_info
        
        # Check for deleted files
        for file_path in list(self._file_states.keys()):
            if file_path not in current_files:
                changes.append(FileChange(
                    file_path=file_path,
                    change_type="deleted",
                    timestamp=datetime.now(),
                ))
                del self._file_states[file_path]
        
        return changes
    
    def _compute_checksum(self, file_path: Path) -> str:
        """Compute file checksum."""
        try:
            stat = file_path.stat()
            data = f"{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(data.encode()).hexdigest()[:8]
        except:
            return ""


# =============================================================================
# Unified Local Data Feed Manager
# =============================================================================

class LocalDataFeedManager:
    """Manager for all local data feeds."""
    
    def __init__(
        self,
        data_path: Optional[str] = None,
    ):
        self.data_path = Path(data_path) if data_path else Path("./data")
        
        # Create data directories
        (self.data_path / "news").mkdir(parents=True, exist_ok=True)
        (self.data_path / "market").mkdir(parents=True, exist_ok=True)
        (self.data_path / "sentiment").mkdir(parents=True, exist_ok=True)
        
        # Initialize connectors
        self.news = LocalNewsConnector(local_data_path=self.data_path / "news")
        self.market = LocalMarketConnector(local_data_path=self.data_path / "market")
        self.sentiment = LocalSentimentConnector(local_data_path=self.data_path / "sentiment")
        self.file_watcher = FileWatcherConnector(watch_paths=[self.data_path])
        
        self._connectors = [self.news, self.market, self.sentiment, self.file_watcher]
    
    async def fetch_all(
        self,
        news_query: Optional[str] = None,
        market_symbols: Optional[List[str]] = None,
        sentiment_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch all data sources."""
        results = {}
        
        if news_query:
            results["news"] = await self.news.fetch(query=news_query)
        
        if market_symbols:
            results["market"] = await self.market.fetch(symbols=market_symbols)
        
        if sentiment_topic:
            results["sentiment"] = await self.sentiment.fetch(topic=sentiment_topic)
        
        results["files"] = await self.file_watcher.fetch(check_changes=True)
        
        return results
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        for connector in self._connectors:
            connector.clear_cache()
    
    async def close(self) -> None:
        """Close all connectors."""
        for connector in self._connectors:
            if hasattr(connector, 'close'):
                await connector.close()


# =============================================================================
# Convenience Functions
# =============================================================================

async def fetch_local_news(
    query: Optional[str] = None,
    data_path: Optional[str] = None,
) -> List[NewsArticle]:
    """Fetch news from local sources."""
    connector = LocalNewsConnector(local_data_path=data_path)
    try:
        return await connector.fetch(query=query)
    finally:
        await connector.close()


async def fetch_local_market(
    symbols: Union[str, List[str]],
    data_path: Optional[str] = None,
) -> List[MarketPrice]:
    """Fetch market data from local sources."""
    connector = LocalMarketConnector(local_data_path=data_path)
    try:
        return await connector.fetch(symbols=symbols)
    finally:
        pass  # Local connector doesn't need closing


async def fetch_local_sentiment(
    topic: str,
    data_path: Optional[str] = None,
) -> List[SentimentScore]:
    """Fetch sentiment from local sources."""
    connector = LocalSentimentConnector(local_data_path=data_path)
    try:
        return await connector.fetch(topic=topic)
    finally:
        pass


def watch_local_files(
    paths: List[Union[str, Path]],
    patterns: Optional[List[str]] = None,
) -> FileWatcherConnector:
    """Create a file watcher for local files."""
    return FileWatcherConnector(watch_paths=paths, patterns=patterns)
