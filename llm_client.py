"""
LLM Client for Swimming Pauls
Supports local models via Ollama/LM Studio and cloud APIs
Also integrates with OpenClaw's configured LLM providers
"""
import os
import json
import asyncio
from typing import Optional, Dict, Any
import aiohttp


class LLMClient:
    """Client for calling LLMs to generate Paul responses."""
    
    def __init__(self, provider: str = "ollama", model: str = "llama3", api_key: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: "ollama", "lmstudio", "openai", "anthropic", or "openclaw"
            model: Model name (e.g., "llama3", "gpt-4", "claude-3-opus")
            api_key: API key for cloud providers (auto-detected from OpenClaw if not provided)
        """
        self.provider = provider.lower()
        self.model = model
        
        # Try to get API key from multiple sources
        self.api_key = api_key or self._get_api_key()
        
        # Default endpoints
        self.endpoints = {
            "ollama": "http://localhost:11434/api/generate",
            "lmstudio": "http://localhost:1234/v1/chat/completions",
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "kimi": "https://api.moonshot.cn/v1/chat/completions",  # Kimi API
            "openclaw": "http://localhost:8080/api/llm",  # OpenClaw local endpoint
        }
        
        self.endpoint = self.endpoints.get(self.provider, self.endpoints["ollama"])
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from environment or OpenClaw config.
        Checks multiple sources in order of priority.
        """
        provider_upper = self.provider.upper()
        
        # 1. Check environment variable for specific provider
        env_key = os.getenv(f"{provider_upper}_API_KEY")
        if env_key:
            return env_key
        
        # 2. Check OpenAI-style env vars
        if self.provider in ["openai", "openclaw"]:
            env_key = os.getenv("OPENAI_API_KEY")
            if env_key:
                return env_key
        
        # 3. Check Anthropic env vars
        if self.provider == "anthropic":
            env_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
            if env_key:
                return env_key
        
        # 4. Check for OpenClaw config file
        openclaw_key = self._get_openclaw_api_key()
        if openclaw_key:
            return openclaw_key
        
        return None
    
    def _get_openclaw_api_key(self) -> Optional[str]:
        """
        Try to read API key from OpenClaw configuration.
        Checks common OpenClaw config locations.
        """
        import yaml
        
        # Possible OpenClaw config locations
        config_paths = [
            os.path.expanduser("~/.openclaw/config.yaml"),
            os.path.expanduser("~/.openclaw/config.yml"),
            "/opt/homebrew/lib/node_modules/openclaw/config.yaml",
            "/usr/local/lib/node_modules/openclaw/config.yaml",
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                        
                        # Try to find API keys in config
                        if 'llm' in config:
                            llm_config = config['llm']
                            
                            # Check for provider-specific key
                            if self.provider in llm_config and 'api_key' in llm_config[self.provider]:
                                return llm_config[self.provider]['api_key']
                            
                            # Check for default key
                            if 'api_key' in llm_config:
                                return llm_config['api_key']
                            
                            # Check for keys nested under providers
                            if 'providers' in llm_config:
                                providers = llm_config['providers']
                                if self.provider in providers and 'api_key' in providers[self.provider]:
                                    return providers[self.provider]['api_key']
                        
                        # Check top-level keys
                        for key in ['openai_api_key', 'anthropic_api_key', 'claude_api_key']:
                            if key in config:
                                provider_name = key.replace('_api_key', '')
                                if self.provider in [provider_name, 'openclaw']:
                                    return config[key]
                except Exception:
                    continue
        
        return None
    
    def auto_select_provider(self) -> tuple:
        """
        Automatically select the best available LLM provider.
        Priority: Kimi (fast, good) > OpenAI > Anthropic > Ollama > LM Studio
        
        Returns:
            Tuple of (provider_name, model_name)
        """
        available = self.list_available_providers()
        
        # Priority order - Kimi first since it's what the user uses
        if available.get("kimi"):
            return ("kimi", "kimi-k2-0714-preview")  # Fast & capable
        
        if available.get("openai"):
            return ("openai", "gpt-4o-mini")  # Cost-effective default
        
        if available.get("anthropic"):
            return ("anthropic", "claude-3-haiku-20240307")  # Fast & cheap
        
        if available.get("ollama"):
            return ("ollama", "llama3")  # Free local option
        
        if available.get("lmstudio"):
            return ("lmstudio", "local-model")  # Local alternative
        
        # Fallback - will likely fail but we try anyway
        return ("ollama", "llama3")
    
    def is_ready(self) -> bool:
        """Check if the LLM client is properly configured and ready to use."""
        if self.provider in ["ollama", "lmstudio"]:
            # Local providers - check if server is running
            available = self.list_available_providers()
            return available.get(self.provider, False)
        else:
            # Cloud providers - check if API key is set
            return self.api_key is not None
    
    def list_available_providers(self) -> Dict[str, bool]:
        """
        Check which LLM providers are available.
        Returns dict of provider names and their availability status.
        """
        available = {
            "ollama": False,
            "lmstudio": False,
            "openai": False,
            "anthropic": False,
            "kimi": False,
        }
        
        # Check Ollama
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:11434", timeout=2)
            available["ollama"] = True
        except:
            pass
        
        # Check LM Studio
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:1234", timeout=2)
            available["lmstudio"] = True
        except:
            pass
        
        # Check API keys
        if os.getenv("OPENAI_API_KEY") or self._get_openclaw_api_key():
            available["openai"] = True
        
        if os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"):
            available["anthropic"] = True
        
        # Check Kimi API key
        if os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY"):
            available["kimi"] = True
        
        return available
    
    async def generate_response(
        self,
        persona_name: str,
        persona_description: str,
        question: str,
        context: str = "",
        memory: str = ""
    ) -> str:
        """
        Generate a response from a Paul persona using LLM.
        
        Args:
            persona_name: Name of the Paul (e.g., "Professor Paul")
            persona_description: Description of their personality
            question: The question being asked
            context: Additional context (files, links, etc.)
            memory: Previous interactions/memory
            
        Returns:
            The LLM-generated response
        """
        system_prompt = f"""You are {persona_name}. {persona_description}

You are participating in a multi-agent prediction pool called "Swimming Pauls". 
Your job is to analyze the question from your unique perspective and provide your opinion.

Guidelines:
- Respond in character based on your persona
- Be concise but insightful (2-4 sentences)
- Include your confidence level (low/medium/high)
- Reference specific factors that influenced your thinking
- It's OK to disagree with the consensus - be authentic to your persona

Current question to analyze:"""

        user_prompt = f"""Question: {question}

{context}

{memory}

Provide your analysis:"""

        try:
            if self.provider == "ollama":
                return await self._call_ollama(system_prompt, user_prompt)
            elif self.provider == "lmstudio":
                return await self._call_lmstudio(system_prompt, user_prompt)
            elif self.provider == "openai":
                return await self._call_openai(system_prompt, user_prompt)
            elif self.provider == "anthropic":
                return await self._call_anthropic(system_prompt, user_prompt)
            elif self.provider == "kimi":
                return await self._call_kimi(system_prompt, user_prompt)
            else:
                return f"[{persona_name}] Unable to generate response - unknown provider"
                
        except Exception as e:
            return f"[{persona_name}] Error generating response: {str(e)[:100]}"
    
    async def _call_ollama(self, system: str, user: str) -> str:
        """Call Ollama local model."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": f"{system}\n\n{user}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150,
                }
            }
            
            async with session.post(self.endpoint, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "No response generated")
                else:
                    return f"Ollama error: {resp.status}"
    
    async def _call_lmstudio(self, system: str, user: str) -> str:
        """Call LM Studio local model."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "temperature": 0.7,
                "max_tokens": 150,
                "stream": False
            }
            
            async with session.post(self.endpoint, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"LM Studio error: {resp.status}"
    
    async def _call_openai(self, system: str, user: str) -> str:
        """Call OpenAI API."""
        if not self.api_key:
            return "OpenAI API key not configured"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            async with session.post(self.endpoint, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"OpenAI error: {resp.status}"
    
    async def _call_anthropic(self, system: str, user: str) -> str:
        """Call Anthropic Claude API."""
        if not self.api_key:
            return "Anthropic API key not configured"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            payload = {
                "model": self.model,
                "max_tokens": 150,
                "system": system,
                "messages": [{"role": "user", "content": user}]
            }
            
            async with session.post(self.endpoint, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["content"][0]["text"]
                else:
                    return f"Anthropic error: {resp.status}"
    
    async def _call_kimi(self, system: str, user: str) -> str:
        """Call Kimi API (Moonshot AI)."""
        if not self.api_key:
            return "Kimi API key not configured. Get one at https://platform.moonshot.cn/"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model or "kimi-k2-0714-preview",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            async with session.post(self.endpoint, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await resp.text()
                    return f"Kimi error: {resp.status} - {error_text[:100]}"


# Persona definitions for LLM context
PERSONA_DEFINITIONS = {
    "Professor Paul": "An academic data analyst who relies on statistics, regression models, and historical patterns. Speaks formally with references to research and methodology. Always cites confidence intervals and statistical significance.",
    
    "Trader Paul": "A fast-paced market trader focused on order flow, volume, and short-term price action. Uses trading slang and technical analysis. Risk-tolerant and action-oriented.",
    
    "Skeptic Paul": "A contrarian who questions consensus and looks for blind spots. Cautious, risk-focused, and always considers tail risks. Often plays devil's advocate.",
    
    "Visionary Paul": "A long-term thinker who sees paradigm shifts and future trends. Intuitive, big-picture oriented. References historical technology adoption curves.",
    
    "Whale Paul": "An institutional investor focused on liquidity, smart money flows, and market structure. Conservative, strategic, and concerned with execution.",
    
    "Degen Paul": "A chaotic crypto degenerate driven by memes, vibes, and YOLO energy. Uses internet slang and emoji. Unpredictable but surprisingly intuitive about sentiment."
}


async def generate_paul_responses_llm(
    question: str,
    pauls: list,
    provider: str = "ollama",
    model: str = "llama3",
    context: str = ""
) -> dict:
    """
    Generate responses from multiple Pauls using LLM.
    
    Args:
        question: The question to analyze
        pauls: List of Paul names (e.g., ["Professor Paul", "Trader Paul"])
        provider: LLM provider
        model: Model name
        context: Additional context
        
    Returns:
        Dict mapping Paul names to their responses
    """
    client = LLMClient(provider=provider, model=model)
    
    tasks = []
    for paul_name in pauls:
        description = PERSONA_DEFINITIONS.get(
            paul_name, 
            "An AI agent with a unique perspective on prediction markets."
        )
        
        task = client.generate_response(
            persona_name=paul_name,
            persona_description=description,
            question=question,
            context=context
        )
        tasks.append((paul_name, task))
    
    # Run all LLM calls concurrently
    results = {}
    for paul_name, task in tasks:
        try:
            response = await asyncio.wait_for(task, timeout=30)
            results[paul_name] = response
        except asyncio.TimeoutError:
            results[paul_name] = f"[{paul_name}] Response timed out"
        except Exception as e:
            results[paul_name] = f"[{paul_name}] Error: {str(e)[:100]}"
    
    return results


# For testing
if __name__ == "__main__":
    async def test():
        client = LLMClient(provider="ollama", model="llama3")
        
        response = await client.generate_response(
            persona_name="Professor Paul",
            persona_description=PERSONA_DEFINITIONS["Professor Paul"],
            question="Should I invest in Bitcoin right now?",
            context="Bitcoin is trading at $67,000, up 15% this month. ETF inflows are strong."
        )
        
        print("Professor Paul says:")
        print(response)
    
    asyncio.run(test())
