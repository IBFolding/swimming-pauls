"""
OpenClaw Skill Integration for Swimming Pauls
Gives Pauls access to OpenClaw skills for enhanced predictions
"""

import os
import sys
import json
import subprocess
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SkillTool:
    """Represents an OpenClaw skill as a tool for Pauls"""
    name: str
    description: str
    emoji: str
    examples: List[str]
    

@dataclass
class PaulPrediction:
    """Structured prediction from a Paul"""
    paul_name: str
    sentiment: str  # bullish/bearish/neutral
    confidence: float  # 0-1
    reasoning: str
    specialty: str = ""
    trading_style: str = ""


class BatchPredictionEngine:
    """
    Batch prediction engine that routes Paul predictions through OpenClaw (Kimi).
    Generates all Paul responses in a single API call for efficiency.
    """
    
    def __init__(self):
        self.model = "kimi/kimi-k2-thinking"
        self.last_source_mode = "unknown"
        
    def batch_predict(self, question: str, pauls: List[Dict[str, Any]]) -> List[PaulPrediction]:
        """
        Generate predictions for all Pauls in a single batch API call.
        
        Args:
            question: The prediction question
            pauls: List of Paul persona dictionaries
            
        Returns:
            List of PaulPrediction objects
        """
        # Reset source mode for this request
        self.last_source_mode = "unknown"

        # Build the batch prompt with all Pauls
        batch_prompt = self._build_batch_prompt(question, pauls)
        
        # Call OpenClaw/Kimi API
        response = self._call_openclaw_api(batch_prompt)
        
        # Parse the structured response
        predictions = self._parse_predictions(response, pauls)
        
        return predictions
    
    def _build_batch_prompt(self, question: str, pauls: List[Dict[str, Any]]) -> str:
        """Build a prompt that includes all Pauls and their unique traits."""
        
        # Limit Pauls in prompt to avoid token limits
        # For large pools, sample representative Pauls
        if len(pauls) > 100:
            # Sample 100 Pauls evenly distributed
            step = len(pauls) // 100
            sampled_pauls = [pauls[i] for i in range(0, len(pauls), step)][:100]
        else:
            sampled_pauls = pauls
        
        prompt = f"""You are orchestrating a multi-agent prediction market simulation called "Swimming Pauls".

QUESTION: {question}

You need to generate predictions from {len(pauls)} different agents (Pauls), each with unique personalities, specialties, and biases.

## PAUL PERSONAS (showing {len(sampled_pauls)} representative examples):

"""
        
        for i, paul in enumerate(sampled_pauls):
            prompt += f"""
### PAUL {i+1}: {paul.get('name', f'Paul-{i}')}
- Trading Style: {paul.get('trading_style', 'Unknown')}
- Risk Profile: {paul.get('risk_profile', 'Unknown')}
- Confidence Base: {paul.get('confidence_base', 0.5):.2f}
- Specialties: {', '.join(paul.get('specialties', [])[:3])}
- Backstory: {paul.get('backstory', 'No backstory')[:100]}...
"""
        
        if len(pauls) > len(sampled_pauls):
            prompt += f"\n... and {len(pauls) - len(sampled_pauls)} more Pauls with similar diverse traits.\n"
        
        prompt += """

## YOUR TASK:

Generate a prediction for EACH of the """ + str(len(pauls)) + """ Pauls based on their unique personality, risk profile, and cognitive strengths. Each Paul should respond differently based on their traits.

IMPORTANT: Respond ONLY with a valid JSON array. No markdown, no explanations outside the JSON.

Each prediction must include:
- paul_name: The exact name of the Paul
- sentiment: One of "bullish", "bearish", or "neutral"
- confidence: A float between 0.0 and 1.0 (based on their confidence_base and personality)
- reasoning: A brief explanation (1-2 sentences) in the voice of that Paul, reflecting their personality

The JSON format should be:
[
  {"paul_name": "Alpha Trader", "sentiment": "bullish", "confidence": 0.85, "reasoning": "The momentum is undeniable. I'm seeing breakout patterns everywhere."},
  {"paul_name": "Beta Analyst", "sentiment": "neutral", "confidence": 0.6, "reasoning": "Data is mixed. Waiting for clearer signals before taking a position."},
  ...
]

Generate predictions for ALL """ + str(len(pauls)) + """ Pauls now."""
        
        return prompt
    
    def _call_openclaw_api(self, prompt: str) -> str:
        """Call OpenClaw API to get batch predictions."""
        try:
            # Try to use openclaw CLI if available
            import subprocess
            import tempfile
            
            # Write prompt to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_path = f.name
            
            # Try using openclaw ask or similar command
            # First, let's try the openclaw CLI
            result = subprocess.run(
                ['openclaw', 'ask', prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.last_source_mode = "openclaw_cli"
                return result.stdout.strip()
            
            # Fallback: try to use the model directly via HTTP API
            return self._call_kimi_api(prompt)
            
        except Exception as e:
            print(f"OpenClaw API call failed: {e}")
            return self._call_kimi_api(prompt)
    
    def _call_kimi_api(self, prompt: str) -> str:
        """Call Kimi API directly as fallback."""
        try:
            import urllib.request
            import urllib.error
            import os
            
            # Check for API key
            api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('KIMI_API_KEY')
            
            if not api_key:
                # Return mock data for testing
                self.last_source_mode = "mock"
                return self._generate_mock_response(prompt)
            
            # OpenRouter API endpoint for Kimi
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://swimming-pauls.local",
                "X-Title": "Swimming Pauls Batch Predictions"
            }
            
            data = {
                "model": "kimi/kimi-k2-thinking",
                "messages": [
                    {"role": "system", "content": "You are a multi-agent prediction system. Respond only with valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 8000
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                self.last_source_mode = "openrouter_kimi"
                return result['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"Kimi API call failed: {e}")
            self.last_source_mode = "mock"
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock predictions for testing when API is unavailable."""
        # Extract Paul count from prompt
        import re
        match = re.search(r'Generate predictions for ALL (\d+) Pauls', prompt)
        count = int(match.group(1)) if match else 50
        
        # Extract Paul names from prompt
        names = re.findall(r'### PAUL \d+: ([^\n]+)', prompt)
        if not names:
            names = [f"Paul-{i}" for i in range(count)]
        
        predictions = []
        sentiments = ["bullish", "bearish", "neutral"]
        
        for name in names[:count]:
            # Generate somewhat realistic prediction based on name hash
            name_hash = sum(ord(c) for c in name) % 100
            
            if name_hash < 40:
                sentiment = "bullish"
            elif name_hash < 70:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            confidence = 0.4 + (name_hash % 50) / 100
            
            reasonings = {
                "bullish": [
                    "The momentum is building. Technicals look strong.",
                    "Smart money is accumulating. I'm following the whales.",
                    "Fundamentals are solid. This is a no-brainer.",
                    "Breaking resistance levels. Time to ride the wave."
                ],
                "bearish": [
                    "Seeing distribution patterns. Time to be cautious.",
                    "Overbought conditions suggest a pullback is coming.",
                    "Risk-off sentiment is growing. Protect your capital.",
                    "The narrative is shifting. Don't fight the trend."
                ],
                "neutral": [
                    "Mixed signals. Waiting for clearer direction.",
                    "Consolidation phase. Patience is key here.",
                    "Data is inconclusive. Sitting this one out.",
                    "Too much uncertainty. Better to wait and see."
                ]
            }
            
            reasoning = random.choice(reasonings[sentiment])
            
            predictions.append({
                "paul_name": name,
                "sentiment": sentiment,
                "confidence": round(confidence, 2),
                "reasoning": reasoning
            })
        
        return json.dumps(predictions)
    
    def _parse_predictions(self, response: str, pauls: List[Dict[str, Any]]) -> List[PaulPrediction]:
        """Parse the JSON response into PaulPrediction objects."""
        predictions = []
        
        try:
            # Clean up response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            
            if isinstance(data, list):
                for item in data:
                    pred = PaulPrediction(
                        paul_name=item.get('paul_name', 'Unknown'),
                        sentiment=item.get('sentiment', 'neutral').lower(),
                        confidence=float(item.get('confidence', 0.5)),
                        reasoning=item.get('reasoning', 'No reasoning provided'),
                        specialty=item.get('specialty', ''),
                        trading_style=item.get('trading_style', '')
                    )
                    predictions.append(pred)
            elif isinstance(data, dict) and 'predictions' in data:
                for item in data['predictions']:
                    pred = PaulPrediction(
                        paul_name=item.get('paul_name', 'Unknown'),
                        sentiment=item.get('sentiment', 'neutral').lower(),
                        confidence=float(item.get('confidence', 0.5)),
                        reasoning=item.get('reasoning', 'No reasoning provided'),
                        specialty=item.get('specialty', ''),
                        trading_style=item.get('trading_style', '')
                    )
                    predictions.append(pred)
                    
        except json.JSONDecodeError as e:
            print(f"Failed to parse predictions JSON: {e}")
            # Fallback: generate predictions based on Pauls
            self.last_source_mode = "rule_fallback"
            predictions = self._generate_fallback_predictions(pauls)
        except Exception as e:
            print(f"Error parsing predictions: {e}")
            self.last_source_mode = "rule_fallback"
            predictions = self._generate_fallback_predictions(pauls)
        
        return predictions
    
    def _generate_fallback_predictions(self, pauls: List[Dict[str, Any]]) -> List[PaulPrediction]:
        """Generate fallback predictions when parsing fails."""
        predictions = []
        
        for paul in pauls:
            # Determine sentiment based on risk profile and randomness
            risk = paul.get('risk_profile', 'MODERATE')
            confidence = paul.get('confidence_base', 0.5)
            
            # Risk profile affects sentiment distribution
            if risk == 'ULTRA_AGGRESSIVE' or risk == 'DEGEN':
                weights = [0.5, 0.3, 0.2]  # More bullish
            elif risk == 'AGGRESSIVE':
                weights = [0.4, 0.35, 0.25]
            elif risk == 'CONSERVATIVE' or risk == 'ULTRA_CONSERVATIVE':
                weights = [0.2, 0.4, 0.4]  # More bearish/neutral
            else:
                weights = [0.33, 0.33, 0.34]
            
            sentiments = ['bullish', 'bearish', 'neutral']
            sentiment = random.choices(sentiments, weights=weights)[0]
            
            # Generate reasoning based on trading style
            style = paul.get('trading_style', 'SWING_TRADER')
            reasonings = {
                'SCALPER': ["Quick momentum play.", "Scalping the volatility."],
                'SWING_TRADER': ["Swing setup looks good.", "Technical pattern forming."],
                'POSITION_TRADER': ["Long-term trend intact.", "Fundamentals support this."],
                'ALGORITHMIC': ["Signal strength is high.", "Model says go."],
                'QUANTITATIVE': ["Statistical edge detected.", "Quant model triggered."],
                'EVENT_DRIVEN': ["Catalyst incoming.", "Event setup is compelling."],
                'MOMENTUM': ["Momentum is accelerating.", "Trend is your friend."],
                'CONTRARIAN': ["Crowd is wrong here.", "Contrarian opportunity."],
                'VALUE': ["Undervalued opportunity.", "Value play emerging."],
            }
            
            reasoning = random.choice(reasonings.get(style, ["Analysis complete.", "Decision made."]))
            
            predictions.append(PaulPrediction(
                paul_name=paul.get('name', 'Unknown'),
                sentiment=sentiment,
                confidence=round(confidence, 2),
                reasoning=reasoning,
                specialty=', '.join(paul.get('specialties', [])[:2]),
                trading_style=style
            ))
        
        return predictions


class OpenClawSkillBridge:
    """
    Bridge between Swimming Pauls and OpenClaw skills.
    Allows individual Pauls to call skills during deliberation.
    """
    
    def __init__(self):
        self.available_skills = self._discover_skills()
        self.tool_registry = self._build_tool_registry()
        self.batch_engine = BatchPredictionEngine()
        
    def batch_predict(self, question: str, pauls: List[Dict[str, Any]]) -> List[PaulPrediction]:
        """
        Generate predictions for all Pauls in a single batch call.
        
        Args:
            question: The prediction question
            pauls: List of Paul persona dictionaries
            
        Returns:
            List of PaulPrediction objects with sentiment, confidence, and reasoning
        """
        return self.batch_engine.batch_predict(question, pauls)

    def batch_predict_with_meta(self, question: str, pauls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate predictions with metadata about the prediction source.
        """
        predictions = self.batch_engine.batch_predict(question, pauls)
        return {
            "predictions": predictions,
            "source_mode": self.batch_engine.last_source_mode
        }
        
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
                
        return False
    
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


    def get_diary_entries(self, paul_name: str, days: int = 7, entry_types: list = None) -> list:
        """Get diary entries for a Paul from the REM backfill system."""
        try:
            from rem_backfill import REMBackfillEngine
            engine = REMBackfillEngine()
            entries = engine.get_diary_timeline(paul_name, days, entry_types)
            return [e.to_dict() for e in entries]
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_world_timeline(self, days: int = 1, entry_types: list = None) -> list:
        """Get world timeline with all Pauls' activities."""
        try:
            from rem_backfill import REMBackfillEngine
            engine = REMBackfillEngine()
            return engine.get_world_timeline(days, entry_types)
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_pauls_with_diaries(self) -> list:
        """Get list of Pauls who have diary entries."""
        try:
            from rem_backfill import REMBackfillEngine
            engine = REMBackfillEngine()
            return engine.get_pauls_with_entries()
        except Exception as e:
            return [{"error": str(e)}]
