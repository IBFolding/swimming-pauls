"""
Web Research Module for Swimming Pauls
Enables Pauls to gather fresh data from the internet before predicting
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx
from urllib.parse import quote_plus


@dataclass
class SearchResult:
    """A web search result."""
    title: str
    url: str
    snippet: str
    source: str
    timestamp: datetime


@dataclass
class WebPage:
    """Scraped web page content."""
    url: str
    title: str
    content: str
    summary: str
    key_points: List[str]
    scraped_at: datetime


class WebResearcher:
    """Research agent that gathers web data for Pauls."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.cache: Dict[str, WebPage] = {}
    
    async def search_and_summarize(
        self,
        query: str,
        max_results: int = 5
    ) -> str:
        """
        Search the web and return a summary for the Pauls.
        
        Args:
            query: Search query (e.g., "Bitcoin price news today")
            max_results: Number of sources to check
            
        Returns:
            Summarized research findings
        """
        try:
            # Search for relevant pages
            search_results = await self._search(query, max_results)
            
            if not search_results:
                return "No recent web data available for this query."
            
            # Scrape top results
            pages = []
            for result in search_results[:max_results]:
                try:
                    page = await self._scrape(result.url)
                    if page:
                        pages.append(page)
                except Exception as e:
                    continue
            
            # Summarize findings
            summary = self._summarize_pages(pages, query)
            return summary
            
        except Exception as e:
            return f"Research error: {str(e)}"
    
    async def _search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[SearchResult]:
        """
        Search the web using multiple search engines.
        Falls back to alternative sources if main fails.
        """
        results = []
        
        # Try DuckDuckGo HTML scraper (no API key needed)
        try:
            ddg_results = await self._search_duckduckgo(query, max_results)
            results.extend(ddg_results)
        except:
            pass
        
        # Try SearXNG instances (privacy-friendly, no API key)
        if len(results) < max_results:
            try:
                searx_results = await self._search_searx(query, max_results - len(results))
                results.extend(searx_results)
            except:
                pass
        
        # Fallback: Try to get data from specific sites directly
        if not results:
            results = await self._search_direct_sites(query)
        
        return results[:max_results]
    
    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int
    ) -> List[SearchResult]:
        """Search DuckDuckGo (no API key required)."""
        encoded_query = quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = await self.client.get(url, headers=headers)
        
        if response.status_code != 200:
            return []
        
        # Simple parsing (in production, use BeautifulSoup)
        results = []
        html = response.text
        
        # Look for result links
        import re
        
        # Extract titles and URLs
        title_pattern = r'<a[^>]*class="result__a"[^>]*>(.*?)</a>'
        url_pattern = r'href="/l/\?kh=-?\d+&amp;u=([^"]+)"'
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
        
        titles = re.findall(title_pattern, html)
        urls = re.findall(url_pattern, html)
        snippets = re.findall(snippet_pattern, html)
        
        # Clean HTML tags
        def clean_html(text):
            text = re.sub(r'<[^>]+>', '', text)
            text = text.replace('&quot;', '"').replace('&amp;', '&')
            return text.strip()
        
        for i in range(min(len(titles), len(urls), max_results)):
            try:
                from urllib.parse import unquote
                actual_url = unquote(urls[i])
                
                results.append(SearchResult(
                    title=clean_html(titles[i]),
                    url=actual_url,
                    snippet=clean_html(snippets[i]) if i < len(snippets) else "",
                    source="DuckDuckGo",
                    timestamp=datetime.now()
                ))
            except:
                continue
        
        return results
    
    async def _search_searx(
        self,
        query: str,
        max_results: int
    ) -> List[SearchResult]:
        """Search SearXNG instances (privacy-friendly)."""
        # Public SearXNG instances
        instances = [
            "https://search.sapti.me",
            "https://search.bus-hit.me",
            "https://search.neet.works",
        ]
        
        for instance in instances:
            try:
                url = f"{instance}/search?q={quote_plus(query)}&format=json"
                response = await self.client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for result in data.get("results", [])[:max_results]:
                        results.append(SearchResult(
                            title=result.get("title", ""),
                            url=result.get("url", ""),
                            snippet=result.get("content", ""),
                            source=result.get("engine", "SearXNG"),
                            timestamp=datetime.now()
                        ))
                    
                    return results
            except:
                continue
        
        return []
    
    async def _search_direct_sites(
        self,
        query: str
    ) -> List[SearchResult]:
        """Fallback: Check specific relevant sites directly."""
        results = []
        
        # Determine which sites to check based on query keywords
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["bitcoin", "crypto", "ethereum", "btc", "eth"]):
            # Check CoinGecko for crypto data
            try:
                response = await self.client.get(
                    "https://api.coingecko.com/api/v3/coins/bitcoin",
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    price = data.get("market_data", {}).get("current_price", {}).get("usd", "N/A")
                    change_24h = data.get("market_data", {}).get("price_change_percentage_24h", "N/A")
                    
                    results.append(SearchResult(
                        title=f"Bitcoin Price: ${price:,.2f} ({change_24h:+.2f}% 24h)",
                        url="https://coingecko.com",
                        snippet=f"Current Bitcoin price data. 24h change: {change_24h:.2f}%",
                        source="CoinGecko",
                        timestamp=datetime.now()
                    ))
            except:
                pass
        
        if any(word in query_lower for word in ["stock", "market", "nasdaq", "sp500", "trade"]):
            # Could add Yahoo Finance or similar here
            pass
        
        return results
    
    async def _scrape(self, url: str) -> Optional[WebPage]:
        """Scrape a webpage and extract key information."""
        # Check cache first
        if url in self.cache:
            return self.cache[url]
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = await self.client.get(url, headers=headers, timeout=10.0)
            
            if response.status_code != 200:
                return None
            
            html = response.text
            
            # Extract title
            import re
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else "No title"
            title = re.sub(r'\s+', ' ', title)  # Clean whitespace
            
            # Extract main content (simplified)
            # Remove scripts, styles, nav, footer
            content = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<nav[^>]*>.*?</nav>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<footer[^>]*>.*?</footer>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Extract text from paragraphs and headings
            text_parts = re.findall(r'<(?:p|h[1-6])[^>]*>(.*?)</(?:p|h[1-6])>', content, re.DOTALL | re.IGNORECASE)
            
            # Clean HTML tags and normalize
            full_text = ' '.join(text_parts)
            full_text = re.sub(r'<[^>]+>', ' ', full_text)  # Remove HTML
            full_text = re.sub(r'\s+', ' ', full_text).strip()  # Normalize whitespace
            full_text = full_text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            # Truncate if too long
            if len(full_text) > 10000:
                full_text = full_text[:10000] + "..."
            
            # Generate summary (first few sentences)
            sentences = full_text.split('. ')
            summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else full_text
            
            # Extract key points (sentences with numbers or key terms)
            key_points = []
            for sentence in sentences[:10]:
                if any(char.isdigit() for char in sentence) or any(word in sentence.lower() for word in ["price", "up", "down", "increase", "decrease", "growth", "decline"]):
                    if len(sentence) > 20:  # Filter out fragments
                        key_points.append(sentence.strip())
                if len(key_points) >= 5:
                    break
            
            page = WebPage(
                url=url,
                title=title,
                content=full_text,
                summary=summary,
                key_points=key_points,
                scraped_at=datetime.now()
            )
            
            # Cache it
            self.cache[url] = page
            
            return page
            
        except Exception as e:
            return None
    
    def _summarize_pages(self, pages: List[WebPage], query: str) -> str:
        """Summarize scraped pages into a research brief."""
        if not pages:
            return "No web data available."
        
        summary_parts = [f"WEB RESEARCH SUMMARY for: '{query}'\n"]
        summary_parts.append(f"Sources checked: {len(pages)}\n")
        
        # Add key findings from each source
        for i, page in enumerate(pages[:3], 1):
            summary_parts.append(f"\n--- Source {i}: {page.title} ---")
            summary_parts.append(f"URL: {page.url}")
            summary_parts.append(f"Summary: {page.summary[:300]}...")
            
            if page.key_points:
                summary_parts.append("Key Points:")
                for point in page.key_points[:3]:
                    summary_parts.append(f"  • {point}")
        
        # Add overall synthesis
        summary_parts.append("\n--- SYNTHESIS ---")
        summary_parts.append("Recent web data shows various perspectives on this topic.")
        summary_parts.append("The Pauls should consider this external context alongside their expertise.")
        
        return '\n'.join(summary_parts)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Convenience function for the Pauls
async def get_web_context(query: str) -> str:
    """
    Quick function to get web research context for a query.
    
    Usage:
        context = await get_web_context("Bitcoin price prediction")
    """
    researcher = WebResearcher()
    try:
        result = await researcher.search_and_summarize(query, max_results=3)
        return result
    finally:
        await researcher.close()


# For testing
if __name__ == "__main__":
    async def test():
        result = await get_web_context("Bitcoin price today")
        print(result)
    
    asyncio.run(test())
