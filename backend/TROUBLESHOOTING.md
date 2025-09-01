# AI Dietitian Backend - Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Pip Installation Errors

#### Error: `KeyError: '__version__'`
**Problem**: This error occurs when a package tries to access a version attribute that doesn't exist, often due to Python 3.13+ compatibility issues.

**Solutions**:
```bash
# Option 1: Use the installation script
python install_deps.py

# Option 2: Install packages one by one
pip install fastapi
pip install uvicorn[standard]
pip install python-dotenv
pip install pydantic
pip install openai

# Option 3: Use the minimal requirements
pip install -r requirements-minimal.txt
```

#### Error: `subprocess-exited-with-error`
**Problem**: Build tools or compilation issues with native packages.

**Solutions**:
```bash
# Update build tools
pip install --upgrade pip setuptools wheel

# Install system dependencies (macOS)
brew install openssl readline sqlite3 xz zlib

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-dev build-essential libssl-dev libffi-dev
```

### 2. Python Version Compatibility

#### Python 3.13+ Issues
**Problem**: Some packages may not be fully compatible with Python 3.13+.

**Solutions**:
```bash
# Option 1: Use Python 3.11 or 3.12
pyenv install 3.11.9
pyenv local 3.11.9

# Option 2: Create virtual environment with specific Python version
python3.11 -m venv .venv
source .venv/bin/activate

# Option 3: Use conda
conda create -n dietitian python=3.11
conda activate dietitian
```

### 3. LangGraph Installation Issues

#### Error: `No module named 'langgraph'`
**Problem**: LangGraph installation failed or version incompatibility.

**Solutions**:
```bash
# Try different versions
pip install langgraph==0.0.20
pip install langgraph==0.1.0
pip install langgraph>=0.2.0

# Install from source
pip install git+https://github.com/langchain-ai/langgraph.git

# Use fallback mode (system will work without LangGraph)
python start.py
```

#### Error: `ImportError: cannot import name 'StateGraph'`
**Problem**: LangGraph version mismatch or incomplete installation.

**Solutions**:
```bash
# Uninstall and reinstall
pip uninstall langgraph
pip install langgraph>=0.2.0

# Check installed version
pip show langgraph
```

### 4. OpenAI Package Issues

#### Error: `No module named 'openai'`
**Problem**: OpenAI package not installed or version mismatch.

**Solutions**:
```bash
# Install latest version
pip install openai>=1.60.0

# Install specific version
pip install openai==1.3.7

# Check compatibility
python -c "import openai; print(openai.__version__)"
```

### 5. Database Connection Issues

#### Error: `No module named 'supabase'`
**Problem**: Supabase client not installed.

**Solutions**:
```bash
# Install Supabase client
pip install supabase>=2.8.0

# Alternative: Use requests for basic HTTP calls
pip install requests
```

### 6. Virtual Environment Issues

#### Error: `Permission denied` or `Command not found`
**Problem**: Virtual environment not activated or permission issues.

**Solutions**:
```bash
# Create new virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Check if activated
which python
pip list
```

### 7. Port Already in Use

#### Error: `Address already in use`
**Problem**: Port 8000 is already occupied.

**Solutions**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 🔧 Step-by-Step Recovery

### Complete Reset and Reinstall
```bash
# 1. Deactivate virtual environment
deactivate

# 2. Remove virtual environment
rm -rf .venv

# 3. Create new virtual environment
python3 -m venv .venv

# 4. Activate
source .venv/bin/activate

# 5. Upgrade pip
pip install --upgrade pip

# 6. Install dependencies step by step
python install_deps.py
```

### Minimal Working Setup
```bash
# 1. Install only essential packages
pip install fastapi uvicorn python-dotenv

# 2. Test basic functionality
python start.py

# 3. Check if server starts
curl http://localhost:8000/health
```

## 📋 Dependency Status Check

Run this to check what's working:
```bash
python start.py
```

This will show you:
- ✅ Available packages and versions
- ❌ Missing packages
- 🔧 Current system status

## 🚀 Alternative Startup Methods

### Method 1: Simple Mode (Recommended for testing)
```bash
python start.py
```

### Method 2: Minimal Mode
```bash
python main-simple.py
```

### Method 3: Full Mode (when all dependencies are available)
```bash
python main.py
```

## 🔍 Debug Information

### Check Python Environment
```bash
python --version
pip --version
which python
pip list
```

### Check Package Versions
```bash
python -c "
import sys
print(f'Python: {sys.version}')
try:
    import fastapi
    print(f'FastAPI: {fastapi.__version__}')
except ImportError:
    print('FastAPI: Not installed')
try:
    import langgraph
    print(f'LangGraph: {langgraph.__version__}')
except ImportError:
    print('LangGraph: Not installed')
"
```

### Environment Variables
```bash
# Check if .env file exists
ls -la .env*

# Check environment variables
echo $PYTHONPATH
echo $VIRTUAL_ENV
```

## 📞 Getting Help

### 1. Check the logs
```bash
# Run with verbose logging
python start.py 2>&1 | tee backend.log
```

### 2. Common error patterns
- **ImportError**: Package not installed or version mismatch
- **AttributeError**: Package version incompatibility
- **PermissionError**: Virtual environment or file permission issues
- **ConnectionError**: Network or service availability issues

### 3. Next steps
1. Try the installation script: `python install_deps.py`
2. Use simple mode: `python start.py`
3. Check dependency status at: `http://localhost:8000/dependencies`
4. Review the logs for specific error messages

## 🎯 Success Indicators

Your backend is working correctly when:
- ✅ Server starts without errors
- ✅ Health check returns `{"status": "healthy"}`
- ✅ API docs are available at `/docs`
- ✅ No import errors in the console
- ✅ All endpoints respond correctly

---

**Remember**: The system is designed to work in fallback mode even with missing dependencies. Start with the simple mode and gradually add packages as needed.





