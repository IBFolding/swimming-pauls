"""
Swimming Pauls - Data Tools Integration
Integrates all 18 data tools into the Paul prediction system.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from skills.data_tools import TOOLS, execute_tool, ToolResult


class DataToolsIntegration:
    """Integrates data tools with Paul predictions."""
    
    def __init__(self):
        self.tool_usage_stats = {}
        self.research_cache = {}
        
    async def research_topic(self, topic: str, tools: List[str] = None) -> Dict[str, Any]:
        """
        Research a topic using multiple data tools.
        
        Args:
            topic: The topic to research (e.g., "BTC price prediction")
            tools: List of tool names to use (default: auto-select based on topic)
            
        Returns:
            Research results from all tools
        """
        # Auto-select tools based on topic keywords
        if not tools:
            tools = self._select_tools_for_topic(topic)
        
        results = {}
        tasks = []
        
        for tool_name in tools:
            if tool_name in TOOLS:
                task = self._execute_with_timeout(tool_name, topic)
                tasks.append((tool_name, task))
        
        # Execute all tools concurrently
        for tool_name, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=10.0)
                results[tool_name] = {
                    "success": result.success,
                    "data": result.data,
                    "source": result.source,
                    "timestamp": result.timestamp
                }
                if result.success:
                    self.tool_usage_stats[tool_name] = self.tool_usage_stats.get(tool_name, 0) + 1
            except asyncio.TimeoutError:
                results[tool_name] = {"success": False, "error": "Timeout", "data": None}
            except Exception as e:
                results[tool_name] = {"success": False, "error": str(e), "data": None}
        
        # Store in research cache (shared across all Pauls)
        cache_key = f"research:{topic.lower().replace(' ', '_')}:{datetime.now().strftime('%Y%m%d')}"
        self.research_cache[cache_key] = {
            "topic": topic,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "tools_used": list(results.keys())
        }
        
        return {
            "topic": topic,
            "tools_used": len(results),
            "successful_tools": sum(1 for r in results.values() if r.get("success")),
            "results": results,
            "cache_key": cache_key
        }
    
    async def _execute_with_timeout(self, tool_name: str, topic: str) -> ToolResult:
        """Execute a tool with timeout handling."""
        # Determine the right method and parameters based on tool
        if tool_name == "web_search":
            return await execute_tool(tool_name, query=topic, limit=5)
        elif tool_name == "crypto_price":
            symbol = self._extract_symbol(topic) or "BTC"
            return await execute_tool(tool_name, symbol=symbol)
        elif tool_name == "stock_price":
            symbol = self._extract_symbol(topic) or "AAPL"
            return await execute_tool(tool_name, symbol=symbol)
        elif tool_name == "news":
            return await execute_tool(tool_name, query=topic)
        elif tool_name == "social_sentiment":
            return await execute_tool(tool_name, keyword=self._extract_symbol(topic) or topic)
        elif tool_name == "onchain":
            token = self._extract_symbol(topic) or "ETH"
            return await execute_tool(tool_name, token=token)
        elif tool_name == "dex_volume":
            token = self._extract_symbol(topic) or "UNI"
            return await execute_tool(tool_name, token=token)
        elif tool_name == "whale_tracking":
            token = self._extract_symbol(topic) or "BTC"
            return await execute_tool(tool_name, token=token)
        elif tool_name == "gas_price":
            return await execute_tool(tool_name, chain="ethereum")
        elif tool_name == "token_unlocks":
            token = self._extract_symbol(topic) or "ARB"
            return await execute_tool(tool_name, token=token)
        elif tool_name == "options_flow":
            symbol = self._extract_symbol(topic) or "SPY"
            return await execute_tool(tool_name, symbol=symbol)
        elif tool_name == "futures":
            symbol = self._extract_symbol(topic) or "BTC"
            return await execute_tool(tool_name, symbol=symbol)
        elif tool_name == "forex":
            return await execute_tool(tool_name, base="USD", quote="EUR")
        elif tool_name == "google_trends":
            return await execute_tool(tool_name, keyword=topic)
        elif tool_name == "sec_filings":
            ticker = self._extract_symbol(topic) or "AAPL"
            return await execute_tool(tool_name, ticker=ticker)
        elif tool_name == "weather":
            return await execute_tool(tool_name, location="New York")
        elif tool_name == "election_polls":
            return await execute_tool(tool_name, race="president")
        elif tool_name == "sports_odds":
            return await execute_tool(tool_name, sport="nfl")
        elif tool_name == "economic_calendar":
            return await execute_tool(tool_name, country="US")
        else:
            return ToolResult(success=False, data=None, error=f"Unknown tool: {tool_name}")
    
    def _select_tools_for_topic(self, topic: str) -> List[str]:
        """Auto-select relevant tools based on topic keywords."""
        topic_lower = topic.lower()
        tools = []
        
        # Crypto-related
        if any(kw in topic_lower for kw in ["btc", "eth", "sol", "crypto", "token", "defi", "nft"]):
            tools.extend(["crypto_price", "onchain", "dex_volume", "whale_tracking", "social_sentiment"])
        
        # Stock-related
        if any(kw in topic_lower for kw in ["stock", "aapl", "tsla", "spy", "nasdaq", "dow"]):
            tools.extend(["stock_price", "options_flow", "sec_filings"])
        
        # Trading/price related
        if any(kw in topic_lower for kw in ["price", "trading", "pump", "dump", "bull", "bear"]):
            tools.extend(["crypto_price", "futures", "gas_price"])
        
        # News/sentiment related
        if any(kw in topic_lower for kw in ["news", "event", "announcement", "fud", "fomo"]):
            tools.extend(["news", "social_sentiment", "google_trends"])
        
        # Macro/economic
        if any(kw in topic_lower for kw in ["fed", "inflation", "cpi", "rate", "economy", "macro"]):
            tools.extend(["economic_calendar", "forex", "futures"])
        
        # Election/politics
        if any(kw in topic_lower for kw in ["election", "vote", "trump", "biden"]):
            tools.extend(["election_polls", "news"])
        
        # Sports/gambling
        if any(kw in topic_lower for kw in ["sports", "bet", "odds", "game", "super bowl"]):
            tools.extend(["sports_odds"])
        
        # Default tools if no specific match
        if not tools:
            tools = ["web_search", "news", "social_sentiment"]
        
        return list(set(tools))  # Remove duplicates
    
    def _extract_symbol(self, topic: str) -> Optional[str]:
        """Extract a ticker symbol from the topic."""
        import re
        # Look for common patterns: $BTC, BTC, #BTC, etc.
        patterns = [
            r'\$([A-Z]{2,10})',  # $BTC
            r'\b([A-Z]{2,5})\b',  # BTC (standalone)
            r'#([A-Z]{2,10})',  # #BTC
        ]
        for pattern in patterns:
            match = re.search(pattern, topic.upper())
            if match:
                return match.group(1)
        return None
    
    def get_research_summary(self, cache_key: str) -> Optional[Dict]:
        """Get cached research results."""
        return self.research_cache.get(cache_key)
    
    def get_tool_stats(self) -> Dict[str, int]:
        """Get tool usage statistics."""
        return self.tool_usage_stats.copy()
    
    async def get_crypto_ohlc(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """Get OHLC data for charting."""
        tool = TOOLS.get("crypto_price")
        if tool:
            result = await tool.get_ohlc(symbol, days)
            return {
                "success": result.success,
                "data": result.data,
                "source": result.source
            }
        return {"success": False, "data": None, "error": "Tool not found"}


# Global instance
data_tools = DataToolsIntegration()


async def research_for_pauls(topic: str, paul_specialties: List[str] = None) -> Dict[str, Any]:
    """
    Main entry point: Research a topic for Paul predictions.
    
    This function is called by the Paul system when making predictions.
    Research is SHARED across all Pauls (cached).
    
    Args:
        topic: The prediction topic/question
        paul_specialties: List of Paul specialties to prioritize tools for
        
    Returns:
        Research data for Pauls to use in predictions
    """
    # Adjust tools based on Paul specialties
    tools = None
    if paul_specialties:
        tools = []
        for specialty in paul_specialties:
            if specialty in ["Momentum Trading", "Day Trader"]:
                tools.extend(["crypto_price", "futures", "options_flow"])
            elif specialty in ["Macro Research", "Fundamental"]:
                tools.extend(["economic_calendar", "forex", "news", "sec_filings"])
            elif specialty in ["Quantitative Analysis", "Data Scientist"]:
                tools.extend(["onchain", "dex_volume", "whale_tracking", "google_trends"])
            elif specialty in ["Meme Coin Hunting", "Degen"]:
                tools.extend(["social_sentiment", "dex_volume", "token_unlocks"])
            elif specialty in ["On-Chain Analysis"]:
                tools.extend(["onchain", "whale_tracking", "gas_price"])
        tools = list(set(tools)) if tools else None
    
    return await data_tools.research_topic(topic, tools)


if __name__ == "__main__":
    async def test():
        print("Testing data tools integration...")
        
        # Test crypto research
        result = await research_for_pauls("Will BTC reach $100k this month?", ["Momentum Trading"])
        print(f"\nResearch for 'BTC $100k':")
        print(f"Tools used: {result['tools_used']}")
        print(f"Successful: {result['successful_tools']}")
        print(f"Cache key: {result['cache_key']}")
        
        # Test macro research
        result = await research_for_pauls("Will Fed raise rates?", ["Macro Research"])
        print(f"\nResearch for 'Fed rates':")
        print(f"Tools used: {result['tools_used']}")
        
        # Get stats
        stats = data_tools.get_tool_stats()
        print(f"\nTool usage stats: {stats}")
    
    asyncio.run(test())
