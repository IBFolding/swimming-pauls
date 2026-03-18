"""
Web Intelligence Module for Swimming Pauls
Multi-source data gathering for informed predictions.
100% local - no APIs required, uses public sources.

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlparse
import xml.etree.ElementTree as ET


@dataclass
class WebResult:
    """Result from web search/scrape."""
    source: str
    title: str
    url: str
    snippet: str
    timestamp: Optional[str] = None
    relevance_score: float = 0.0


@dataclass
class TrendData:
    """Trending topic data."""
    topic: str
    volume: int
    sentiment: str  # POSITIVE, NEGATIVE, NEUTRAL
    velocity: str   # RISING, FALLING, STABLE
    related: List[str]


class WebIntelligence:
    """
    Multi-source web intelligence for Pauls.
    No API keys needed - uses public endpoints.
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def search(self, query: str, limit: int = 10) -> List[WebResult]:
        """
        Multi-engine web search.
        Tries multiple sources, aggregates results.
        """
        results = []
        
        # Try multiple sources concurrently
        tasks = [
            self._search_duckduckgo(query, limit),
            self._search_searxng(query, limit),
            self._search_bing(query, limit),
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate and deduplicate
        seen_urls = set()
        for result_set in search_results:
            if isinstance(result_set, list):
                for result in result_set:
                    if result.url not in seen_urls:
                        seen_urls.add(result.url)
                        results.append(result)
                        
        # Sort by relevance and return top
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    async def _search_duckduckgo(self, query: str, limit: int) -> List[WebResult]:
        """Search via DuckDuckGo HTML."""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            async with self.session.get(url) as response:
                html = await response.text()
                
                results = []
                # Parse results (simplified)
                links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>', html)
                snippets = re.findall(r'<a class="result__snippet"[^>]*>([^<]+)</a>', html)
                
                for i, (link, title) in enumerate(links[:limit]):
                    snippet = snippets[i] if i < len(snippets) else ""
                    results.append(WebResult(
                        source="DuckDuckGo",
                        title=self._clean_html(title),
                        url=self._clean_url(link),
                        snippet=self._clean_html(snippet),
                        relevance_score=1.0 - (i * 0.1)
                    ))
                    
                return results
        except Exception as e:
            return []
    
    async def _search_searxng(self, query: str, limit: int) -> List[WebResult]:
        """Search via SearXNG instances."""
        # List of public SearXNG instances
        instances = [
            "https://search.sapti.me",
            "https://search.bus-hit.me",
            "https://search.projectsegfault.com",
        ]
        
        for instance in instances:
            try:
                url = f"{instance}/search?q={quote_plus(query)}&format=json"
                
                async with self.session.get(url) as response:
                    data = await response.json()
                    
                    results = []
                    for i, result in enumerate(data.get('results', [])[:limit]):
                        results.append(WebResult(
                            source="SearXNG",
                            title=result.get('title', ''),
                            url=result.get('url', ''),
                            snippet=result.get('content', ''),
                            relevance_score=result.get('score', 1.0 - (i * 0.1))
                        ))
                    return results
            except:
                continue
                
        return []
    
    async def _search_bing(self, query: str, limit: int) -> List[WebResult]:
        """Search via Bing (no API key needed for basic)."""
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}"
            
            async with self.session.get(url) as response:
                html = await response.text()
                
                results = []
                # Parse Bing results (simplified)
                titles = re.findall(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>([^<]+)</a></h2>', html)
                
                for i, (link, title) in enumerate(titles[:limit]):
                    results.append(WebResult(
                        source="Bing",
                        title=self._clean_html(title),
                        url=self._clean_url(link),
                        snippet="",
                        relevance_score=1.0 - (i * 0.1)
                    ))
                    
                return results
        except:
            return []
    
    async def get_wikipedia_summary(self, topic: str) -> Optional[str]:
        """Get Wikipedia summary for a topic."""
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(topic.replace(' ', '_'))}"
            
            async with self.session.get(url) as response:
                data = await response.json()
                return data.get('extract', '')
        except:
            return None
    
    async def get_reddit_discussions(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search Reddit discussions.
        Uses Reddit's JSON API (no auth needed for search).
        """
        try:
            url = f"https://www.reddit.com/search.json?q={quote_plus(query)}&limit={limit}"
            
            async with self.session.get(url, headers={'User-Agent': 'SwimmingPauls/1.0'}) as response:
                data = await response.json()
                
                posts = []
                for post in data.get('data', {}).get('children', []):
                    p = post['data']
                    posts.append({
                        'title': p.get('title', ''),
                        'subreddit': p.get('subreddit', ''),
                        'upvotes': p.get('ups', 0),
                        'comments': p.get('num_comments', 0),
                        'url': f"https://reddit.com{p.get('permalink', '')}",
                        'snippet': p.get('selftext', '')[:200] if p.get('selftext') else ''
                    })
                    
                return posts
        except:
            return []
    
    async def get_github_activity(self, repo: str) -> Optional[Dict]:
        """
        Get GitHub repository activity.
        Public repos don't need auth.
        """
        try:
            url = f"https://api.github.com/repos/{repo}"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'open_issues': data.get('open_issues_count', 0),
                    'last_updated': data.get('updated_at', ''),
                    'language': data.get('language', ''),
                    'description': data.get('description', '')
                }
        except:
            return None
    
    async def get_trends(self, query: str) -> TrendData:
        """
        Analyze trending data from multiple sources.
        """
        # Search multiple sources
        web_results = await self.search(query, limit=20)
        reddit_posts = await self.get_reddit_discussions(query, limit=10)
        
        # Calculate metrics
        total_mentions = len(web_results) + len(reddit_posts)
        
        # Simple sentiment analysis based on keywords
        positive_words = ['bullish', 'growth', 'increase', 'gain', 'moon', 'pump', 'strong', 'adoption']
        negative_words = ['bearish', 'crash', 'decrease', 'loss', 'dump', 'weak', 'fud', 'concern']
        
        positive_count = 0
        negative_count = 0
        
        for result in web_results:
            text = (result.title + " " + result.snippet).lower()
            positive_count += sum(1 for w in positive_words if w in text)
            negative_count += sum(1 for w in negative_words if w in text)
            
        for post in reddit_posts:
            text = (post['title'] + " " + post['snippet']).lower()
            positive_count += sum(1 for w in positive_words if w in text)
            negative_count += sum(1 for w in negative_words if w in text)
        
        # Determine sentiment
        if positive_count > negative_count * 1.5:
            sentiment = "POSITIVE"
        elif negative_count > positive_count * 1.5:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
            
        # Related topics (from search suggestions)
        related = list(set([r.title.split()[0] for r in web_results[:5]]))
        
        return TrendData(
            topic=query,
            volume=total_mentions,
            sentiment=sentiment,
            velocity="RISING" if total_mentions > 50 else "STABLE",
            related=related
        )
    
    async def scrape_article(self, url: str) -> Optional[str]:
        """
        Scrape article content.
        Extracts main text, removes boilerplate.
        """
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                html = await response.text()
                
                # Remove scripts and styles
                html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
                html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
                
                # Extract text
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Get first 2000 chars (main content usually at start)
                return text[:2000]
        except:
            return None
    
    async def get_rss_feed(self, feed_url: str, limit: int = 5) -> List[Dict]:
        """Fetch and parse RSS feed."""
        try:
            async with self.session.get(feed_url) as response:
                content = await response.text()
                
                root = ET.fromstring(content)
                items = []
                
                # Handle RSS 2.0
                for item in root.findall('.//item')[:limit]:
                    items.append({
                        'title': item.findtext('title', ''),
                        'link': item.findtext('link', ''),
                        'description': item.findtext('description', '')[:300],
                        'pub_date': item.findtext('pubDate', '')
                    })
                    
                return items
        except:
            return []
    
    def _clean_html(self, text: str) -> str:
        """Clean HTML entities from text."""
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&#39;', "'")
        return text
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL."""
        if url.startswith('//'):
            url = 'https:' + url
        return url


# Paul-specific intelligence gathering
class PaulIntelligenceGatherer:
    """
    Specialized intelligence gathering for different Paul types.
    """
    
    def __init__(self, web_intel: WebIntelligence):
        self.web = web_intel
        
    async def gather_for_trader(self, asset: str) -> Dict:
        """Gather trading intelligence."""
        results = await asyncio.gather(
            self.web.search(f"{asset} price analysis today"),
            self.web.get_reddit_discussions(f"{asset} trading", limit=3),
            self.web.get_trends(asset)
        )
        
        return {
            'market_sentiment': results[2].sentiment,
            'trend_velocity': results[2].velocity,
            'discussions': results[1],
            'news_count': len(results[0])
        }
        
    async def gather_for_professor(self, topic: str) -> Dict:
        """Gather academic/fundamental intelligence."""
        results = await asyncio.gather(
            self.web.get_wikipedia_summary(topic),
            self.web.search(f"{topic} research analysis filetype:pdf", limit=5),
            self.web.get_reddit_discussions(f"{topic} long term", limit=3)
        )
        
        return {
            'wikipedia_summary': results[0],
            'research_links': results[1],
            'community_thoughts': results[2]
        }
        
    async def gather_for_developer(self, project: str) -> Dict:
        """Gather dev/tech intelligence."""
        results = await asyncio.gather(
            self.web.get_github_activity(project),
            self.web.search(f"{project} github commits updates"),
            self.web.get_reddit_discussions(f"{project} development", limit=3)
        )
        
        return {
            'github_stats': results[0],
            'recent_updates': results[1][:3],
            'dev_discussions': results[2]
        }


# Integration with existing skill_bridge.py
def extend_skill_bridge():
    """
    Extend the OpenClaw skill bridge with web intelligence.
    Add this to skill_bridge.py
    """
    return """
    # In skill_bridge.py, add to OpenClawSkillBridge:
    
    async def enrich_with_web_intel(self, paul_name: str, question: str) -> Dict:
        \"\"\"Gather web intelligence for a Paul.\"\"\"
        async with WebIntelligence() as web:
            gatherer = PaulIntelligenceGatherer(web)
            
            # Determine what to gather based on Paul type
            if 'Trader' in paul_name or 'Whale' in paul_name:
                # Extract asset from question
                asset = self._extract_asset(question)
                if asset:
                    return await gatherer.gather_for_trader(asset)
                    
            elif 'Professor' in paul_name or 'Analyst' in paul_name:
                return await gatherer.gather_for_professor(question[:50])
                
            elif 'Dev' in paul_name or 'Protocol' in paul_name:
                project = self._extract_project(question)
                if project:
                    return await gatherer.gather_for_developer(project)
            
            # Default: general search
            results = await web.search(question, limit=5)
            trends = await web.get_trends(question[:30])
            
            return {
                'web_results': results,
                'trend_data': trends
            }
    """


if __name__ == "__main__":
    async def test():
        async with WebIntelligence() as web:
            print("🔍 Testing Web Intelligence...\n")
            
            # Test search
            print("Searching for 'Ethereum ETF approval'...")
            results = await web.search("Ethereum ETF approval", limit=3)
            for r in results:
                print(f"  {r.source}: {r.title[:60]}...")
            
            # Test trends
            print("\n📈 Analyzing trends for 'Bitcoin'...")
            trends = await web.get_trends("Bitcoin")
            print(f"  Sentiment: {trends.sentiment}")
            print(f"  Volume: {trends.volume} mentions")
            print(f"  Velocity: {trends.velocity}")
            
            # Test Reddit
            print("\n💬 Reddit discussions about 'Solana'...")
            posts = await web.get_reddit_discussions("Solana", limit=3)
            for p in posts:
                print(f"  r/{p['subreddit']}: {p['title'][:50]}... ({p['upvotes']} upvotes)")
    
    asyncio.run(test())
