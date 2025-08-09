#!/usr/bin/env python3
"""
Quick start script for Hear! Hear! Bot
"""

import os
import sys
from pathlib import Path

def main():
    """Quick start function"""
    print("🤖 Hear! Hear! Bot - Quick Start")
    print("=" * 40)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\nTo get started:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("\n2. Edit .env and add your Discord bot token")
        print("3. Run this script again")
        return
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_path = Path(".venv")
        if venv_path.exists():
            print("🔧 Activating virtual environment...")
            python_cmd = str(venv_path / "bin" / "python")
        else:
            python_cmd = "python"
    else:
        python_cmd = sys.executable
    
    print("🚀 Starting bot...")
    os.system(f"{python_cmd} main.py")

if __name__ == "__main__":
    main()
