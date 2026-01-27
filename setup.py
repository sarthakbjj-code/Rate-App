#!/usr/bin/env python3
"""One-click setup script for Procurement Intelligence System."""
import os
import subprocess
import sys


def setup():
    """Setup the application."""
    print("🚀 Setting up Procurement Intelligence System...\n")
    
    # Install Python packages
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Install Playwright browsers
    print("\n🌐 Installing browser drivers...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("✅ Browser drivers installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Failed to install browser drivers: {e}")
        print("   You can install manually later with: python -m playwright install chromium")
    
    # Create directories
    print("\n📁 Creating directories...")
    directories = ['data', 'logs', 'exports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print(f"✅ Directories created: {', '.join(directories)}")
    
    # Setup database
    print("\n💾 Setting up database...")
    try:
        subprocess.check_call([sys.executable, "scripts/setup_database.py"])
        print("✅ Database setup complete")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup database: {e}")
        return False
    
    # Create .env file
    print("\n⚙️  Creating configuration...")
    if not os.path.exists('.env'):
        try:
            with open('.env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ Configuration file created (.env)")
        except Exception as e:
            print(f"⚠️  Warning: Failed to create .env file: {e}")
    else:
        print("✅ Configuration file already exists")
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\n📖 Next steps:")
    print("  1. (Optional) Edit .env file for API keys and settings")
    print("  2. Run: streamlit run web_app/app.py")
    print("  3. Open browser at http://localhost:8501")
    print("\n💡 For help, see docs/SETUP.md")
    
    return True


if __name__ == "__main__":
    try:
        success = setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)
