#!/usr/bin/env python3
"""
Check LLM availability for Swimming Pauls
Shows which LLM providers are available and their configuration status
"""

import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import LLMClient


def check_llm_status():
    """Check and display LLM provider status."""
    print("🔍 Swimming Pauls - LLM Provider Check")
    print("=" * 50)
    
    client = LLMClient()
    available = client.list_available_providers()
    
    print("\n📊 Available Providers:")
    print("-" * 30)
    
    for provider, is_available in available.items():
        status = "✅ Ready" if is_available else "❌ Not Available"
        # Highlight Kimi since it's the user's preferred provider
        highlight = " 👈 Your OpenClaw LLM" if provider == "kimi" and is_available else ""
        print(f"  {provider.upper():12} {status}{highlight}")
    
    print("\n🎯 Auto-Selected Provider:")
    print("-" * 30)
    provider, model = client.auto_select_provider()
    print(f"  Provider: {provider}")
    print(f"  Model: {model}")
    
    # Check if client is ready
    print("\n🔧 Client Status:")
    print("-" * 30)
    if client.is_ready():
        print("  ✅ LLM Client is ready to use")
    else:
        print("  ⚠️  LLM Client not ready")
        print("     Install Ollama: brew install ollama")
        print("     Or set API key: export OPENAI_API_KEY=your_key")
    
    print("\n💡 Usage:")
    print("-" * 30)
    print("  # Use auto-selected provider (Kimi if available)")
    print("  python swimming_pauls.py --predict 'Will BTC pump?'")
    print("")
    print("  # Use Kimi (your OpenClaw LLM)")
    print("  export KIMI_API_KEY=your_key_here")
    print("  python swimming_pauls.py --predict 'Will BTC pump?' --provider kimi")
    print("")
    print("  # Use specific provider")
    print("  python swimming_pauls.py --predict 'Will BTC pump?' --provider openai")
    print("")
    print("  # Use local Ollama (free)")
    print("  python swimming_pauls.py --predict 'Will BTC pump?' --provider ollama")
    print("")
    print("  # See all options")
    print("  python swimming_pauls.py --help")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    check_llm_status()
