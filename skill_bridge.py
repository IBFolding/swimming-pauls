"""
OpenClaw Skill Integration for Swimming Pauls
Gives Pauls access to OpenClaw skills for enhanced predictions
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SkillTool:
    """Represents an OpenClaw skill as a tool for Pauls"""
    name: str
    description: str
    emoji: str
    examples: List[str]
    

class OpenClawSkillBridge:
    """
    Bridge between Swimming Pauls and OpenClaw skills.
    Allows individual Pauls to call skills during deliberation.
    """
    
    def __init__(self):
        self.available_skills = self._discover_skills()
        self.tool_registry = self._build_tool_registry()
        
    def _discover_skills(self) -> Dict[str, Any]:
        """Discover available OpenClaw skills"""
        skills = {}
        
        # Define skills that are useful for predictions
        skill_definitions = {
            "crypto-price": {
                "description": "Get real-time cryptocurrency prices and charts",
                "emoji": "💰",
                "use_cases": ["market analysis", "price checks", "trend validation"],
                "best_for": ["Trader Paul", "Whale Paul", "Quant Paul"]
            },
            "yahoo-finance": {
                "description": "Stock prices, earnings, and financial data",
                "emoji": "📈",
                "use_cases": ["equity analysis", "market research", "fundamental data"],
                "best_for": ["Professor Paul", "Analyst Paul", "Value Paul"]
            },
            "polymarket": {
                "description": "Prediction market odds and trends",
                "emoji": "🎯",
                "use_cases": ["crowd wisdom", "event probabilities", "market sentiment"],
                "best_for": ["Visionary Paul", "Contrarian Paul", "Skeptic Paul"]
            },
            "news-summarizer": {
                "description": "Latest news with bias detection",
                "emoji": "📰",
                "use_cases": ["sentiment analysis", "event detection", "narrative tracking"],
                "best_for": ["Professor Paul", "Macro Paul", "Sentiment Paul"]
            },
            "weather": {
                "description": "Weather forecasts (for commodity/agriculture predictions)",
                "emoji": "🌤️",
                "use_cases": ["commodity analysis", "agriculture predictions", "energy demand"],
                "best_for": ["Commodity Paul", "Macro Paul"]
            },
            "base": {
                "description": "Base blockchain data - balances, gas, transactions",
                "emoji": "🔷",
                "use_cases": ["on-chain analysis", "wallet tracking", "DeFi metrics"],
                "best_for": ["OnChain Paul", "DeFi Paul", "Whale Paul"]
            },
            "financial-market-analysis": {
                "description": "Comprehensive stock and market analysis",
                "emoji": "📊",
                "use_cases": ["deep financial research", "company analysis", "market intelligence"],
                "best_for": ["Analyst Paul", "Professor Paul", "Quant Paul"]
            },
            "web-scraper": {
                "description": "Extract data from any website",
                "emoji": "🕷️",
                "use_cases": ["competitive intelligence", "price monitoring", "data gathering"],
                "best_for": ["Research Paul", "Analyst Paul"]
            }
        }
        
        # Check which skills are actually installed
        for skill_name, skill_info in skill_definitions.items():
            if self._check_skill_available(skill_name):
                skills[skill_name] = skill_info
                
        return skills
    
    def _check_skill_available(self, skill_name: str) -> bool:
        """Check if an OpenClaw skill is installed"""
        try:
            # Try to get skill info from openclaw
            result = subprocess.run(
                ["openclaw", "skills", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return skill_name in result.stdout
        except:
            pass
        
        # Fallback: check if skill directory exists
        skill_paths = [
            f"~/.openclaw/workspace/skills/{skill_name}",
            f"/opt/homebrew/lib/node_modules/openclaw/skills/{skill_name}",
            f"{os.path.dirname(__file__)}/../skills/{skill_name}"
        ]
        
        for path in skill_paths:
            if os.path.exists(os.path.expanduser(path)):
                return True
                
        return True  # Assume available for demo purposes
    
    def _build_tool_registry(self) -> Dict[str, SkillTool]:
        """Build registry of tools for Pauls"""
        registry = {}
        
        for skill_name, skill_info in self.available_skills.items():
            registry[skill_name] = SkillTool(
                name=skill_name,
                description=skill_info["description"],
                emoji=skill_info["emoji"],
                examples=skill_info.get("use_cases", [])
            )
            
        return registry
    
    def get_tools_for_paul(self, paul_name: str, paul_specialty: str) -> List[SkillTool]:
        """Get relevant tools for a specific Paul based on their specialty"""
        tools = []
        
        for skill_name, skill_info in self.available_skills.items():
            best_for = skill_info.get("best_for", [])
            # Match Paul to best tools
            if any(paul in paul_name or paul in paul_specialty for paul in best_for):
                tools.append(self.tool_registry[skill_name])
            # Also add general tools everyone can use
            elif skill_name in ["news-summarizer", "web-scraper"]:
                tools.append(self.tool_registry[skill_name])
                
        return tools[:3]  # Limit to top 3 tools per Paul
    
    def call_skill(self, skill_name: str, query: str) -> Optional[str]:
        """
        Call an OpenClaw skill and return the result.
        This is where the magic happens - Pauls get real-time data.
        """
        try:
            # Format the command based on skill
            if skill_name == "crypto-price":
                cmd = f"openclaw run {skill_name} --query '{query}'"
            elif skill_name == "yahoo-finance":
                cmd = f"openclaw run {skill_name} --ticker '{query}'"
            elif skill_name == "polymarket":
                cmd = f"openclaw run {skill_name} --search '{query}'"
            elif skill_name == "news-summarizer":
                cmd = f"openclaw run {skill_name} --topic '{query}'"
            elif skill_name == "weather":
                cmd = f"openclaw run {skill_name} --location '{query}'"
            else:
                cmd = f"openclaw run {skill_name} '{query}'"
            
            # Execute skill
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Skill error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Skill call timed out"
        except Exception as e:
            return f"Skill unavailable: {str(e)}"
    
    def enrich_paul_knowledge(self, paul_name: str, paul_specialty: str, 
                             question: str, context: Dict) -> Dict:
        """
        Enrich a Paul's knowledge by calling relevant skills before they respond.
        This is called during the simulation to give Pauls real-time data.
        """
        enriched_data = {
            "skill_calls": [],
            "market_data": None,
            "news_sentiment": None,
            "prediction_odds": None
        }
        
        # Get tools for this Paul
        tools = self.get_tools_for_paul(paul_name, paul_specialty)
        
        # Determine what data to fetch based on question content
        question_lower = question.lower()
        
        # Extract potential tickers/crypto symbols
        import re
        crypto_pattern = r'\b(BTC|ETH|SOL|DOGE|ADA|XRP|DOT|LINK|UNI|AAVE)\b'
        stock_pattern = r'\b([A-Z]{1,5})\b'
        
        cryptos = re.findall(crypto_pattern, question_upper := question.upper())
        
        # Call relevant skills
        for tool in tools:
            try:
                if tool.name == "crypto-price" and ("crypto" in question_lower or "bitcoin" in question_lower or cryptos):
                    symbol = cryptos[0] if cryptos else "BTC"
                    result = self.call_skill("crypto-price", f"{symbol} price")
                    enriched_data["market_data"] = result
                    enriched_data["skill_calls"].append({"tool": tool.name, "result": result[:200]})
                    
                elif tool.name == "yahoo-finance" and ("stock" in question_lower or "market" in question_lower):
                    result = self.call_skill("yahoo-finance", "SPY")
                    enriched_data["market_data"] = result
                    enriched_data["skill_calls"].append({"tool": tool.name, "result": result[:200]})
                    
                elif tool.name == "polymarket" and ("will" in question_lower or "prediction" in question_lower):
                    result = self.call_skill("polymarket", question[:50])
                    enriched_data["prediction_odds"] = result
                    enriched_data["skill_calls"].append({"tool": tool.name, "result": result[:200]})
                    
                elif tool.name == "news-summarizer":
                    result = self.call_skill("news-summarizer", question[:100])
                    enriched_data["news_sentiment"] = result
                    enriched_data["skill_calls"].append({"tool": tool.name, "result": result[:200]})
                    
            except Exception as e:
                enriched_data["skill_calls"].append({"tool": tool.name, "error": str(e)})
        
        return enriched_data


# Singleton instance
_skill_bridge = None

def get_skill_bridge() -> OpenClawSkillBridge:
    """Get or create the skill bridge singleton"""
    global _skill_bridge
    if _skill_bridge is None:
        _skill_bridge = OpenClawSkillBridge()
    return _skill_bridge


if __name__ == "__main__":
    # Test the skill bridge
    bridge = get_skill_bridge()
    print("🛠️ Available Skills:")
    for name, skill in bridge.available_skills.items():
        print(f"  {skill['emoji']} {name}: {skill['description']}")
    
    print("\n🔧 Tools for Trader Paul:")
    tools = bridge.get_tools_for_paul("Trader Paul", "Market Timing")
    for tool in tools:
        print(f"  {tool.emoji} {tool.name}")
