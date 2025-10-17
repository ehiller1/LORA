# Python 3.10+ Upgrade Guide

**Date**: January 17, 2025  
**Purpose**: Enable CrewAI and LangChain agent frameworks

---

## 🎯 Why Upgrade?

Python 3.10+ unlocks:
- ✅ **CrewAI** - Multi-agent orchestration framework
- ✅ **LangChain** - Advanced agent workflows
- ✅ **LangGraph** - State machine for complex agents
- ✅ **Latest AI/ML libraries** with full feature support

---

## 📋 Step-by-Step Upgrade

### **Step 1: Install Python 3.11**

#### Option A: Using Homebrew (Recommended)
```bash
# Install Python 3.11
brew install python@3.11

# Verify installation
python3.11 --version
# Should output: Python 3.11.x

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Option B: Using pyenv (For Managing Multiple Versions)
```bash
# Install pyenv
brew install pyenv

# Add to shell config (~/.zshrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.11
pyenv install 3.11.0

# Set globally or locally
pyenv global 3.11.0  # For all projects
# OR
cd /path/to/rmn-lora-system
pyenv local 3.11.0   # Just for this project
```

---

### **Step 2: Create Virtual Environment**

```bash
# Navigate to project
cd /Users/erichillerbrand/Retail\ Media\ Network/CascadeProjects/windsurf-project/rmn-lora-system

# Stop any running streamlit servers
pkill -f streamlit

# Remove old virtual environment if it exists
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Verify you're using Python 3.11
python --version
# Should show: Python 3.11.x
```

---

### **Step 3: Upgrade pip**

```bash
# Upgrade pip to latest
python -m pip install --upgrade pip

# Verify
pip --version
# Should show: pip 25.2 or later
```

---

### **Step 4: Install All Dependencies**

```bash
# Install everything (this will take 5-10 minutes)
pip install -r requirements.txt

# If you get errors, try installing in stages:

# Stage 1: Core dependencies
pip install torch transformers peft accelerate datasets

# Stage 2: Agent frameworks
pip install crewai crewai-tools langchain langchain-openai langchain-core langgraph

# Stage 3: Everything else
pip install -r requirements.txt
```

---

### **Step 5: Verify Installation**

```bash
# Test Python version
python -c "import sys; print(f'Python {sys.version}')"

# Test CrewAI
python -c "import crewai; print(f'CrewAI {crewai.__version__}')"

# Test LangChain
python -c "import langchain; print(f'LangChain {langchain.__version__}')"

# Test Streamlit
python -c "import streamlit; print(f'Streamlit {streamlit.__version__}')"

# Test PyTorch
python -c "import torch; print(f'PyTorch {torch.__version__}')"
```

---

### **Step 6: Restart Your Application**

```bash
# Launch the welcome screen
streamlit run demo/pages/0_welcome.py

# Or launch the main demo
streamlit run demo/streamlit_app.py

# Or launch the admin UI
streamlit run src/ui/lora_admin.py
```

---

## 🔧 Troubleshooting

### **Issue: Command not found: python3.11**

**Solution**: Python 3.11 not in PATH
```bash
# Find where it's installed
which python3.11
# OR
ls /opt/homebrew/bin/python3.11

# Add to PATH manually
export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"
```

---

### **Issue: pip install fails with SSL errors**

**Solution**: Update certificates
```bash
# Install certificates
pip install --upgrade certifi

# Or use Homebrew Python's certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

---

### **Issue: torch installation fails**

**Solution**: Install from PyTorch website
```bash
# For Mac with Apple Silicon (M1/M2/M3)
pip install torch torchvision torchaudio

# For Intel Mac
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

### **Issue: bitsandbytes not available for Mac**

**Solution**: It's Linux-only, comment it out for Mac
```bash
# In requirements.txt, comment out:
# bitsandbytes>=0.41.0

# Or install Mac-compatible fork
pip install bitsandbytes-darwin
```

---

### **Issue: Memory errors during installation**

**Solution**: Install with --no-cache-dir
```bash
pip install --no-cache-dir -r requirements.txt
```

---

## 📊 What Changes

### Before (Python 3.9)
```
✅ Core LoRA system
✅ Storytelling features
✅ RLHF UI
✅ Basic LangChain
❌ CrewAI
❌ LangGraph
❌ Latest agent features
```

### After (Python 3.11)
```
✅ Core LoRA system
✅ Storytelling features
✅ RLHF UI
✅ Full LangChain ecosystem
✅ CrewAI multi-agent
✅ LangGraph workflows
✅ All latest AI features
```

---

## 🚀 Post-Upgrade: Test CrewAI

Create a test file to verify CrewAI works:

```python
# test_crewai.py
from crewai import Agent, Task, Crew

# Create an agent
analyst = Agent(
    role="RMN Budget Analyst",
    goal="Optimize retail media spend",
    backstory="Expert in retail media budget allocation",
    verbose=True
)

# Create a task
task = Task(
    description="Analyze a $2.5M budget allocation across Amazon, Walmart, Target",
    agent=analyst
)

# Create crew
crew = Crew(
    agents=[analyst],
    tasks=[task],
    verbose=True
)

# Run
result = crew.kickoff()
print(result)
```

Run it:
```bash
python test_crewai.py
```

---

## ✅ Success Criteria

After upgrade, you should be able to:

1. ✅ Run `python --version` → Shows Python 3.11.x
2. ✅ Import CrewAI without errors
3. ✅ Import LangChain without errors
4. ✅ Launch all Streamlit UIs
5. ✅ Train LoRA adapters
6. ✅ Run multi-agent workflows

---

## 🎯 Quick Upgrade Command

If you want to do it all at once:

```bash
# Full upgrade script
cd /Users/erichillerbrand/Retail\ Media\ Network/CascadeProjects/windsurf-project/rmn-lora-system

# Install Python 3.11
brew install python@3.11

# Stop streamlit
pkill -f streamlit

# Create fresh venv
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install everything
pip install -r requirements.txt

# Test
python -c "import crewai; import langchain; print('✅ Success!')"

# Launch
streamlit run demo/pages/0_welcome.py
```

---

## 📝 Notes

### Virtual Environment Best Practices
- Always activate venv before working: `source venv/bin/activate`
- Deactivate when done: `deactivate`
- Never commit venv to git (already in .gitignore)

### IDE Configuration
If using VS Code, update Python interpreter:
1. Cmd+Shift+P → "Python: Select Interpreter"
2. Choose `./venv/bin/python`

### Jupyter Notebooks
If using Jupyter, install kernel:
```bash
python -m ipykernel install --user --name=rmn-lora --display-name="RMN LoRA (3.11)"
```

---

## 🆘 Need Help?

If you encounter issues:
1. Check Python version: `python --version`
2. Check pip version: `pip --version`
3. Check venv is activated: `which python` (should show path with `venv`)
4. Try installing dependencies one at a time to isolate the issue

---

**Ready to upgrade?** Follow Step 1 above to get started!
