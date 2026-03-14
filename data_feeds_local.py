"""
Swimming Pauls - Local Data Feeds Module
100% local operation - no APIs, no cloud, no external dependencies

Provides local connectors for:
- Local file reading (PDFs, CSVs, JSON, text)
- RSS feed parsing
- Web scraping (no API keys needed)
- File system monitoring
"""

import asyncio
import json
import os
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

# Optional imports - graceful degradation
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class NewsArticle:
    """News article from local sources."""
    title: str
    source: str
    published_at: datetime
    content: str
    url: Optional[str] = None
    sentiment: Optional[float] = None
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "source": self.source,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "url": self.url,
            "sentiment": self.sentiment,
            "keywords": self.keywords,
        }


@dataclass
class LocalData:
    """Generic local data container."""
    source: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "content": self.content[:1000] + "..." if len(self.content) > 1000 else self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Local Connectors (No APIs Required)
# =============================================================================

class LocalFileConnector:
    """Reads local files - PDFs, CSVs, JSON, TXT, MD."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.json', '.csv', '.pdf', '.html', '.xml'}
    
    def __init__(self, watch_dirs: Optional[List[str]] = None):
        self.watch_dirs = watch_dirs or ["./data"]
        self.cache: Dict[str, LocalData] = {}
        self.last_scan: Dict[str, float] = {}
    
    def read_file(self, filepath: str) -> Optional[LocalData]:
        """Read and parse a single file."""
        path = Path(filepath)
        
        if not path.exists():
            return None
        
        ext = path.suffix.lower()
        
        try:
            if ext == '.pdf' and HAS_PYPDF2:
                return self._read_pdf(path)
            elif ext == '.json':
                return self._read_json(path)
            elif ext == '.csv':
                return self._read_csv(path)
            elif ext in {'.txt', '.md', '.html', '.xml'}:
                return self._read_text(path)
            else:
                # Try as text
                return self._read_text(path)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def _read_pdf(self, path: Path) -> LocalData:
        """Extract text from PDF."""
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        return LocalData(
            source=str(path),
            content=text,
            metadata={"type": "pdf", "pages": len(reader.pages)}
        )
    
    def _read_json(self, path: Path) -> LocalData:
        """Read JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return LocalData(
            source=str(path),
            content=json.dumps(data, indent=2),
            metadata={"type": "json", "keys": list(data.keys()) if isinstance(data, dict) else []}
        )
    
    def _read_csv(self, path: Path) -> LocalData:
        """Read CSV file."""
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        headers = lines[0].strip().split(',') if lines else []
        
        return LocalData(
            source=str(path),
            content=''.join(lines[:100]),  # First 100 lines
            metadata={"type": "csv", "headers": headers, "rows": len(lines) - 1}
        )
    
    def _read_text(self, path: Path) -> LocalData:
        """Read text file."""
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return LocalData(
            source=str(path),
            content=content,
            metadata={"type": path.suffix.lstrip('.'), "size": len(content)}
        )
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[LocalData]:
        """Scan directory for supported files."""
        results = []
        path = Path(directory)
        
        if not path.exists():
            return results
        
        pattern = "**/*" if recursive else "*"
        
        for filepath in path.glob(pattern):
            if filepath.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                data = self.read_file(str(filepath))
                if data:
                    results.append(data)
        
        return results
    
    def watch_directories(self, callback: Optional[Callable] = None, interval: int = 60):
        """Watch directories for changes (polling-based)."""
        import threading
        
        def watcher():
            while True:
                for directory in self.watch_dirs:
                    current_time = time.time()
                    last_time = self.last_scan.get(directory, 0)
                    
                    if current_time - last_time >= interval:
                        files = self.scan_directory(directory)
                        for f in files:
                            if f.source not in self.cache:
                                self.cache[f.source] = f
                                if callback:
                                    callback(f)
                        
                        self.last_scan[directory] = current_time
                
                time.sleep(interval)
        
        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()
        return thread


class RSSConnector:
    """Parse RSS feeds without API keys."""
    
    DEFAULT_FEEDS = [
        # News
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        # Tech
        "https://news.ycombinator.com/rss",
        "https://www.reddit.com/r/technology/.rss",
        # Finance
        "https://www.reddit.com/r/finance/.rss",
    ]
    
    def __init__(self, feeds: Optional[List[str]] = None):
        self.feeds = feeds or self.DEFAULT_FEEDS
        self.cache: Dict[str, List[NewsArticle]] = {}
        self.last_fetch: Dict[str, float] = {}
    
    async def fetch_feed(self, url: str) -> List[NewsArticle]:
        """Fetch and parse a single RSS feed."""
        # Check cache
        now = time.time()
        if url in self.last_fetch and now - self.last_fetch[url] < 300:  # 5 min cache
            return self.cache.get(url, [])
        
        articles = []
        
        if HAS_FEEDPARSER:
            try:
                import feedparser
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:20]:  # Limit to 20 articles
                    article = NewsArticle(
                        title=entry.get('title', 'Untitled'),
                        source=feed.feed.get('title', url),
                        published_at=self._parse_date(entry.get('published', '')),
                        content=entry.get('summary', entry.get('description', '')),
                        url=entry.get('link'),
                        keywords=entry.get('tags', [])
                    )
                    articles.append(article)
            except Exception as e:
                print(f"Error fetching RSS {url}: {e}")
        
        elif HAS_HTTPX:
            # Manual RSS parsing
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=30)
                    articles = self._parse_rss_xml(response.text, url)
            except Exception as e:
                print(f"Error fetching RSS {url}: {e}")
        
        self.cache[url] = articles
        self.last_fetch[url] = now
        return articles
    
    def _parse_rss_xml(self, xml_content: str, source: str) -> List[NewsArticle]:
        """Parse RSS XML manually."""
        articles = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Find all item elements (RSS 2.0)
            for item in root.findall('.//item'):
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                article = NewsArticle(
                    title=title.text if title is not None else 'Untitled',
                    source=source,
                    published_at=self._parse_date(pub_date.text if pub_date is not None else ''),
                    content=description.text if description is not None else '',
                    url=link.text if link is not None else None
                )
                articles.append(article)
        except Exception as e:
            print(f"Error parsing RSS XML: {e}")
        
        return articles
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats."""
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        return datetime.now()
    
    async def fetch_all(self) -> List[NewsArticle]:
        """Fetch all configured RSS feeds."""
        all_articles = []
        
        for url in self.feeds:
            articles = await self.fetch_feed(url)
            all_articles.extend(articles)
        
        # Sort by date
        all_articles.sort(key=lambda x: x.published_at, reverse=True)
        return all_articles[:100]  # Return top 100


class WebScraperConnector:
    """Basic web scraping without API keys."""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.last_fetch: Dict[str, float] = {}
    
    async def scrape_page(self, url: str) -> Dict[str, Any]:
        """Scrape a web page for text content."""
        # Check cache
        now = time.time()
        if url in self.last_fetch and now - self.last_fetch[url] < 600:  # 10 min cache
            return self.cache.get(url, {})
        
        if not HAS_HTTPX:
            return {"error": "httpx not installed"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30, follow_redirects=True)
                
                if HAS_BS4:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text
                    text = soup.get_text()
                    
                    # Clean up
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Get title
                    title = soup.find('title')
                    title_text = title.get_text() if title else ""
                    
                    result = {
                        "url": url,
                        "title": title_text,
                        "content": text[:5000],  # Limit content
                        "word_count": len(text.split()),
                    }
                else:
                    # Basic text extraction
                    text = re.sub('<[^<]+?>', '', response.text)
                    result = {
                        "url": url,
                        "title": "",
                        "content": text[:5000],
                        "word_count": len(text.split()),
                    }
                
                self.cache[url] = result
                self.last_fetch[url] = now
                return result
                
        except Exception as e:
            return {"error": str(e), "url": url}
    
    async def search_site(self, base_url: str, query: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Search within a site for relevant pages."""
        results = []
        
        if not HAS_HTTPX:
            return results
        
        try:
            # Start with base page
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, timeout=30)
                
                if HAS_BS4:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links
                    links = []
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        full_url = urljoin(base_url, href)
                        
                        # Check if link text contains query
                        link_text = a.get_text().lower()
                        if query.lower() in link_text:
                            links.append(full_url)
                    
                    # Scrape relevant pages
                    for url in links[:max_pages]:
                        page = await self.scrape_page(url)
                        if "error" not in page:
                            results.append(page)
        
        except Exception as e:
            print(f"Error searching {base_url}: {e}")
        
        return results


# =============================================================================
# Local Data Feed Manager
# =============================================================================

class LocalDataFeedManager:
    """Manages all local data sources - no APIs, no cloud."""
    
    def __init__(
        self,
        watch_dirs: Optional[List[str]] = None,
        rss_feeds: Optional[List[str]] = None,
    ):
        self.file_connector = LocalFileConnector(watch_dirs)
        self.rss_connector = RSSConnector(rss_feeds)
        self.web_scraper = WebScraperConnector()
    
    async def fetch_all_local_data(self) -> Dict[str, List[Any]]:
        """Fetch all available local data."""
        results = {
            "files": [],
            "rss": [],
            "web": [],
        }
        
        # Scan local files
        for directory in self.file_connector.watch_dirs:
            files = self.file_connector.scan_directory(directory)
            results["files"].extend(files)
        
        # Fetch RSS feeds
        rss_articles = await self.rss_connector.fetch_all()
        results["rss"] = rss_articles
        
        return results
    
    def load_seed_data(self, filepath: str) -> Optional[LocalData]:
        """Load seed data from a file."""
        return self.file_connector.read_file(filepath)
    
    def watch_files(self, callback: Optional[Callable] = None, interval: int = 60):
        """Start watching directories for changes."""
        return self.file_connector.watch_directories(callback, interval)
    
    def get_stats(self) -> Dict[str, int]:
        """Get stats about local data sources."""
        return {
            "watched_directories": len(self.file_connector.watch_dirs),
            "cached_files": len(self.file_connector.cache),
            "rss_feeds": len(self.rss_connector.feeds),
            "rss_cached": sum(len(v) for v in self.rss_connector.cache.values()),
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def load_local_file(filepath: str) -> Optional[LocalData]:
    """Quick function to load a local file."""
    connector = LocalFileConnector()
    return connector.read_file(filepath)


async def fetch_rss_feeds(feeds: Optional[List[str]] = None) -> List[NewsArticle]:
    """Quick function to fetch RSS feeds."""
    connector = RSSConnector(feeds)
    return await connector.fetch_all()


def scan_local_directory(directory: str, recursive: bool = True) -> List[LocalData]:
    """Quick function to scan a directory."""
    connector = LocalFileConnector([directory])
    return connector.scan_directory(directory, recursive)


async def scrape_web_page(url: str) -> Dict[str, Any]:
    """Quick function to scrape a web page."""
    connector = WebScraperConnector()
    return await connector.scrape_page(url)


# =============================================================================
# Demo / Testing
# =============================================================================

async def demo():
    """Demonstrate local data feeds."""
    print("=" * 60)
    print("SWIMMING PAULS - Local Data Feeds Demo")
    print("=" * 60)
    
    # Local files
    print("\n📁 Scanning for local files...")
    connector = LocalFileConnector(["./data", "./documents"])
    
    # Create test file if it doesn't exist
    test_dir = Path("./data")
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "test_article.txt"
    test_file.write_text("""
Netflix Reports Strong Q4 Earnings

Netflix announced better-than-expected earnings for Q4 2025, 
surpassing analyst estimates by 15%. The streaming giant added
8.2 million new subscribers, bringing total membership to 285 million.

Key highlights:
- Revenue: $9.8B (up 13% YoY)
- Operating margin: 22.5%
- Free cash flow: $1.2B
- New content investments: $17B for 2026

Analysts remain bullish on the stock, citing strong content slate
and password sharing crackdown success.
""")
    
    local_data = connector.read_file(str(test_file))
    if local_data:
        print(f"✓ Loaded: {local_data.source}")
        print(f"  Content preview: {local_data.content[:200]}...")
        print(f"  Metadata: {local_data.metadata}")
    
    # RSS feeds
    print("\n📰 Fetching RSS feeds (no API key required)...")
    rss = RSSConnector()
    articles = await rss.fetch_all()
    print(f"✓ Fetched {len(articles)} articles from {len(rss.feeds)} feeds")
    
    if articles:
        print(f"  Latest: {articles[0].title} ({articles[0].source})")
    
    # Stats
    print("\n📊 Data Feed Stats:")
    manager = LocalDataFeedManager()
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Demo complete - all local, no APIs, no cloud!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo())
