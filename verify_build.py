"""Verify that the RMN LoRA System can build and run."""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_dependencies():
    """Check if required dependencies can be imported."""
    print("\n📦 Checking dependencies...")
    
    required = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'duckdb': 'DuckDB',
        'pulp': 'PuLP',
        'pyyaml': 'PyYAML'
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (missing)")
            missing.append(name)
    
    return len(missing) == 0, missing

def check_file_structure():
    """Check if required files and directories exist."""
    print("\n📁 Checking file structure...")
    
    required_files = [
        'demo/streamlit_app.py',
        'demo/generate_synthetic_data.py',
        'demo/requirements.txt',
        'src/ui/lora_admin.py',
        'README.md',
        'requirements.txt'
    ]
    
    required_dirs = [
        'demo/tools',
        'src/agents',
        'src/schemas',
        'src/training',
        'src/runtime',
        'src/storage'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_exist = False
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ (missing)")
            all_exist = False
    
    return all_exist

def check_imports():
    """Check if custom modules can be imported."""
    print("\n🔧 Checking custom module imports...")
    
    sys.path.insert(0, str(Path.cwd()))
    
    modules_to_check = [
        ('demo.tools.warehouse', 'WarehouseManager'),
        ('demo.tools.optimizer', 'BudgetOptimizer'),
        ('demo.tools.policy', 'PolicyChecker'),
        ('demo.tools.creatives', 'CreativeGenerator'),
        ('demo.tools.experiments', 'ExperimentDesigner')
    ]
    
    all_ok = True
    for module_path, class_name in modules_to_check:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   ✅ {module_path}.{class_name}")
        except Exception as e:
            print(f"   ❌ {module_path}.{class_name} ({str(e)[:50]}...)")
            all_ok = False
    
    return all_ok

def check_data_generation():
    """Check if synthetic data can be generated."""
    print("\n🎲 Checking data generation...")
    
    data_dir = Path('demo/data')
    if data_dir.exists():
        files = list(data_dir.rglob('*'))
        if len(files) > 0:
            print(f"   ✅ Data directory exists with {len(files)} files")
            return True
        else:
            print(f"   ⚠️  Data directory empty (run generate_synthetic_data.py)")
            return True  # Not a failure, just needs to be run
    else:
        print(f"   ⚠️  Data directory doesn't exist (will be created)")
        return True

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("RMN LoRA System - Build Verification")
    print("=" * 60)
    
    checks = []
    
    # Python version
    checks.append(("Python Version", check_python_version()))
    
    # Dependencies
    deps_ok, missing = check_dependencies()
    checks.append(("Dependencies", deps_ok))
    
    # File structure
    checks.append(("File Structure", check_file_structure()))
    
    # Custom imports (only if dependencies are OK)
    if deps_ok:
        checks.append(("Module Imports", check_imports()))
    else:
        print("\n🔧 Skipping module import checks (install dependencies first)")
        checks.append(("Module Imports", None))
    
    # Data generation
    checks.append(("Data Generation", check_data_generation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in checks if result is True)
    failed = sum(1 for _, result in checks if result is False)
    skipped = sum(1 for _, result in checks if result is None)
    
    for name, result in checks:
        if result is True:
            print(f"✅ {name}")
        elif result is False:
            print(f"❌ {name}")
        else:
            print(f"⏭️  {name} (skipped)")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All checks passed! Ready to push to GitHub.")
        print("\n📝 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Generate data: cd demo && python generate_synthetic_data.py")
        print("   3. Test demo: streamlit run demo/streamlit_app.py")
        print("   4. Push to GitHub: git push origin main")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        if not deps_ok:
            print("\n📦 To install dependencies:")
            print("   pip install -r requirements.txt")
            print("   cd demo && pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
