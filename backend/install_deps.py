#!/usr/bin/env python3
"""
Dependency Installation Script for AI Dietitian Backend
This script helps install dependencies step by step to resolve version conflicts
Updated for Python 3.13 compatibility
"""

import subprocess
import sys
import os

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

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("⚠️  Warning: Python 3.11+ is recommended for best compatibility")
        return False
    elif version.major == 3 and version.minor >= 13:
        print("⚠️  Python 3.13 detected - using compatible package versions")
        return "python313"
    else:
        print("✅ Python version is compatible")
        return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    return run_command("pip install --upgrade pip", "Upgrading pip")

def install_core_deps(python_version):
    """Install core dependencies first"""
    if python_version == "python313":
        # Use Python 3.13 compatible versions
        core_packages = [
            "fastapi>=0.115.0",
            "uvicorn[standard]>=0.32.0",
            "python-dotenv>=1.0.1",
            "pydantic>=2.10.0",
            "pydantic-settings>=2.8.0",
            "httpx>=0.28.0"
        ]
    else:
        # Use standard versions
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
            return False
    return True

def install_ai_deps(python_version):
    """Install AI-related dependencies"""
    ai_packages = [
        "openai>=1.60.0"
    ]
    
    for package in ai_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: {package} installation failed, continuing...")
    
    return True

def install_langgraph(python_version):
    """Install LangGraph with fallback options"""
    print("\n🔄 Installing LangGraph...")
    
    # Try different versions
    versions_to_try = [
        "langgraph>=0.2.0",
        "langgraph==0.1.0",
        "langgraph==0.0.20",
        "langgraph"
    ]
    
    for version in versions_to_try:
        if run_command(f"pip install {version}", f"Installing {version}"):
            return True
    
    print("❌ LangGraph installation failed. The system will use fallback mode.")
    return False

def install_data_deps(python_version):
    """Install data analysis dependencies with Python 3.13 compatibility"""
    print("\n🔄 Installing data analysis packages...")
    
    if python_version == "python313":
        # Python 3.13 compatible versions
        data_packages = [
            "pandas>=2.2.0",
            "numpy>=1.26.0",
            "matplotlib>=3.10.0",
            "seaborn>=0.13.0"
        ]
    else:
        # Standard versions
        data_packages = [
            "pandas>=2.2.0",
            "numpy>=1.26.0",
            "matplotlib>=3.9.0",
            "seaborn>=0.14.0"
        ]
    
    success_count = 0
    for package in data_packages:
        if run_command(f"pip install {package}", f"Installing {package}"):
            success_count += 1
        else:
            print(f"⚠️  Warning: {package} installation failed")
    
    print(f"✅ {success_count}/{len(data_packages)} data packages installed successfully")
    return success_count > 0

def install_database_deps():
    """Install database-related dependencies"""
    db_packages = [
        "supabase>=2.8.0"
    ]
    
    for package in db_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: {package} installation failed")
    
    return True

def install_dev_deps():
    """Install development dependencies"""
    dev_packages = [
        "pytest>=8.2.0",
        "black>=24.10.0"
    ]
    
    for package in dev_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: {package} installation failed")
    
    return True

def test_imports():
    """Test if key packages can be imported"""
    print("\n🧪 Testing package imports...")
    
    test_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("openai", "openai")
    ]
    
    all_good = True
    for package, import_name in test_packages:
        try:
            __import__(import_name)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} import failed: {e}")
            all_good = False
    
    return all_good

def main():
    """Main installation process"""
    print("🚀 AI Dietitian Backend - Dependency Installation")
    print("=" * 50)
    
    # Check Python version
    python_version = check_python_version()
    if not python_version:
        print("❌ Python version not compatible. Please use Python 3.11+")
        return False
    
    # Upgrade pip
    if not upgrade_pip():
        print("❌ Pip upgrade failed. Please check your Python installation.")
        return False
    
    # Install dependencies step by step
    if not install_core_deps(python_version):
        print("❌ Core dependencies installation failed.")
        return False
    
    if not install_ai_deps(python_version):
        print("⚠️  AI dependencies installation had issues, but continuing...")
    
    if not install_langgraph(python_version):
        print("⚠️  LangGraph installation failed, system will use fallback mode.")
    
    if not install_data_deps(python_version):
        print("⚠️  Data analysis packages installation had issues.")
    
    if not install_database_deps():
        print("⚠️  Database dependencies installation had issues.")
    
    if not install_dev_deps():
        print("⚠️  Development dependencies installation had issues.")
    
    # Test imports
    if not test_imports():
        print("❌ Some packages failed to import. Please check the errors above.")
        return False
    
    print("\n🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Set up your environment variables (copy from env.example)")
    print("2. Test the backend: python start.py")
    print("3. Check the API docs at: http://localhost:8000/docs")
    
    if python_version == "python313":
        print("\n⚠️  Note: Running with Python 3.13 - some features may be limited")
        print("Consider using Python 3.11 or 3.12 for full compatibility")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
