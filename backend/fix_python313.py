#!/usr/bin/env python3
"""
Quick Fix Script for Python 3.13 Compatibility Issues
This script fixes the specific seaborn and numpy version conflicts you're experiencing
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Fix Python 3.13 compatibility issues"""
    print("🔧 Python 3.13 Compatibility Fix")
    print("=" * 40)
    
    # Check Python version
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 13:
        print("⚠️  This script is designed for Python 3.13+")
        print("Your Python version should work with the standard requirements.txt")
        return
    
    print("✅ Python 3.13 detected - applying compatibility fixes")
    
    # Step 1: Uninstall problematic packages
    print("\n🧹 Cleaning up problematic packages...")
    packages_to_remove = [
        "seaborn",
        "numpy", 
        "pandas",
        "matplotlib"
    ]
    
    for package in packages_to_remove:
        run_command(f"pip uninstall -y {package}", f"Removing {package}")
    
    # Step 2: Install Python 3.13 compatible versions
    print("\n📦 Installing Python 3.13 compatible versions...")
    
    # Core packages that work with Python 3.13
    core_packages = [
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "python-dotenv>=1.0.1",
        "pydantic>=2.10.0",
        "pydantic-settings>=2.8.0",
        "httpx>=0.28.0"
    ]
    
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: {package} installation failed")
    
    # Data packages with Python 3.13 compatibility
    data_packages = [
        "numpy>=1.26.0,<1.27.0",  # Python 3.13 compatible
        "pandas>=2.2.0,<2.3.0",   # Python 3.13 compatible
        "matplotlib>=3.10.0",      # Python 3.13 compatible
        "seaborn>=0.13.0,<0.14.0" # Python 3.13 compatible
    ]
    
    print("\n📊 Installing data analysis packages...")
    for package in data_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: {package} installation failed")
    
    # AI packages
    ai_packages = [
        "openai>=1.60.0"
    ]
    
    print("\n🤖 Installing AI packages...")
    for package in ai_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: {package} installation failed")
    
    # Database packages
    db_packages = [
        "supabase>=2.8.0"
    ]
    
    print("\n🗄️ Installing database packages...")
    for package in db_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: {package} installation failed")
    
    # Test imports
    print("\n🧪 Testing package imports...")
    test_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("openai", "openai"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn")
    ]
    
    all_good = True
    for package, import_name in test_packages:
        try:
            __import__(import_name)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} import failed: {e}")
            all_good = False
    
    if all_good:
        print("\n🎉 All packages are working correctly!")
        print("\n📋 Next steps:")
        print("1. Test the backend: python start.py")
        print("2. Check the API docs at: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some packages failed to import")
        print("The system will work in fallback mode")
        print("Try running: python start.py")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)





