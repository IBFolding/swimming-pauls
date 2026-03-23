#!/usr/bin/env python3
"""
Swimming Pauls - Setup Wizard
Guides new users through initial setup
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    print("\n" + "=" * 60)
    print("🦷 SWIMMING PAULS - SETUP WIZARD")
    print("=" * 60)
    print()

def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required")
        print(f"   Current: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required packages."""
    print("\n📦 Installing dependencies...")
    
    req_file = Path(__file__).parent / 'requirements.txt'
    if not req_file.exists():
        print("⚠️  requirements.txt not found")
        return False
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(req_file)],
            check=True
        )
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create required directories."""
    print("\n📁 Creating directories...")
    
    dirs = ['data', 'data/results', 'logs', 'config']
    base = Path(__file__).parent
    
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    return True

def copy_config():
    """Copy example config to config.yaml."""
    print("\n⚙️  Setting up configuration...")
    
    base = Path(__file__).parent
    example = base / 'config.example.yaml'
    config = base / 'config.yaml'
    
    if config.exists():
        print("✅ config.yaml already exists")
        return True
    
    if example.exists():
        import shutil
        shutil.copy(example, config)
        print("✅ config.yaml created from example")
        return True
    else:
        print("⚠️  config.example.yaml not found")
        return False

def test_imports():
    """Test that key imports work."""
    print("\n🧪 Testing imports...")
    
    required = ['websockets', 'httpx', 'numpy', 'pandas']
    failed = []
    
    for module in required:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  Missing modules: {', '.join(failed)}")
        print("   Run: pip install " + " ".join(failed))
        return False
    
    return True

def run_diagnostics():
    """Run system diagnostics."""
    print("\n🔍 Running diagnostics...")
    
    try:
        import psutil
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024**3)
        
        print(f"  Available RAM: {available_gb:.1f} GB")
        
        if available_gb < 4:
            print("  ⚠️  Low memory - recommend 8GB+ for 100+ Pauls")
        elif available_gb < 8:
            print("  ✅ Good for 100-500 Pauls")
        else:
            print(f"  ✅ Excellent - can run 1000+ Pauls")
        
        # Estimate max Pauls
        max_pauls = int(available_gb / 0.05)
        print(f"  Estimated max Pauls: ~{max_pauls}")
        
    except ImportError:
        print("  ℹ️  psutil not installed - skipping memory check")
    
    return True

def print_next_steps():
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Start Swimming Pauls:")
    print("   python start.py")
    print()
    print("2. Open in browser:")
    print("   http://localhost:3005")
    print()
    print("3. Run a test prediction:")
    print("   python openclaw-skill/skill.py 'Will BTC go up?'")
    print()
    print("4. View leaderboard:")
    print("   python leaderboard.py")
    print()
    print("For help: python start.py --help")
    print()

def main():
    print_banner()
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Ask to install dependencies
    print("\nInstall dependencies? (y/n): ", end='')
    if input().lower() == 'y':
        if not install_dependencies():
            print("\n⚠️  Continuing without dependencies...")
    
    # Create directories
    create_directories()
    
    # Copy config
    copy_config()
    
    # Test imports
    test_imports()
    
    # Run diagnostics
    run_diagnostics()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
