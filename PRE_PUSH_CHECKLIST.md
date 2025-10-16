# Pre-Push Checklist ✅

## Quick Reference

Run this before pushing to GitHub: https://github.com/ehiller1/LORA

## Automated Checks

### 1. Run Verification Script

```bash
python3 verify_build.py
```

**Expected Results**:
- ✅ Python 3.8+ installed
- ✅ File structure complete
- ✅ Data directory exists
- ⚠️ Dependencies (optional - not needed for GitHub)

### 2. Check Git Status

```bash
git status
```

**Look for**:
- No uncommitted sensitive files (.env, config.yaml, etc.)
- No large model files (>100MB)
- No personal data in examples

## Manual Checks

### Code Quality

- [ ] No hardcoded API keys or passwords
- [ ] No personal information in comments
- [ ] No TODO comments with sensitive info
- [ ] Import statements work (no broken imports)
- [ ] No debug print statements left in production code

### Documentation

- [ ] README.md is up to date
- [ ] QUICK_START_GUIDE.md has correct commands
- [ ] All referenced files exist
- [ ] No broken internal links
- [ ] Version numbers are consistent

### Configuration

- [ ] `.gitignore` covers all sensitive files
- [ ] `requirements.txt` has all dependencies with versions
- [ ] `demo/requirements.txt` is separate and correct
- [ ] No absolute paths in code (use relative paths)
- [ ] Environment variables documented

### Data & Models

- [ ] No large files (models, datasets) staged
- [ ] Synthetic data generator works
- [ ] Sample data is anonymized
- [ ] Schema mappings are generic (no client names)

### Security

- [ ] No `.env` files committed
- [ ] No `config.yaml` with secrets
- [ ] No API keys in code
- [ ] No database credentials
- [ ] No personal access tokens
- [ ] `.gitignore` includes sensitive patterns

## File Structure Verification

### Required Files ✅

```
✅ README.md
✅ QUICK_START_GUIDE.md
✅ requirements.txt
✅ setup.py
✅ Makefile
✅ .gitignore
✅ verify_build.py
✅ PUSH_TO_GITHUB.sh
```

### Required Directories ✅

```
✅ demo/
✅ src/agents/
✅ src/schemas/
✅ src/training/
✅ src/runtime/
✅ src/storage/
✅ src/ui/
✅ src/nde_rater/
✅ config/
✅ scripts/
✅ tests/
```

### Documentation Files ✅

```
✅ UI_DESIGN_SPEC.md
✅ ADMIN_UI_GUIDE.md
✅ UNIFIED_UI_ARCHITECTURE.md
✅ UI_IMPLEMENTATION_SUMMARY.md
✅ UI_VISUAL_GUIDE.md
✅ FINAL_UI_DELIVERABLES.md
✅ STYLING_INTEGRATION.md
✅ GITHUB_SETUP.md
✅ PRE_PUSH_CHECKLIST.md (this file)
```

## Size Check

### Check Repository Size

```bash
# Check total size
du -sh .

# Check largest files
find . -type f -size +10M -exec ls -lh {} \; | awk '{print $5, $9}'

# Check .git size
du -sh .git
```

**Limits**:
- Individual file: <100MB (GitHub limit)
- Repository: <1GB recommended
- .git directory: <500MB recommended

### Large Files to Exclude

These should be in `.gitignore`:
- `models/base/*` - Base models (multi-GB)
- `models/adapters/*` - Trained adapters (10-50MB each)
- `data/raw/*` - Raw data files
- `*.pth`, `*.bin`, `*.safetensors` - Model weights
- `*.db` - Database files
- `*.log` - Log files

## Test Locally

### 1. Test Main Demo

```bash
cd demo
python generate_synthetic_data.py
streamlit run streamlit_app.py
```

**Verify**:
- [ ] App launches without errors
- [ ] All 6 tabs load
- [ ] Data harmonization works
- [ ] Optimization runs
- [ ] No import errors

### 2. Test Admin Console

```bash
streamlit run src/ui/lora_admin.py
```

**Verify**:
- [ ] App launches without errors
- [ ] All 4 tabs load
- [ ] Training job creation works
- [ ] Federation composition displays
- [ ] No import errors

### 3. Test Imports

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from demo.tools.warehouse import WarehouseManager
from demo.tools.optimizer import BudgetOptimizer
print('✅ All imports successful')
"
```

## Git Commands Reference

### Check What Will Be Committed

```bash
# Dry run - see what would be added
git add -n .

# See file count
git add -n . | wc -l

# Check status
git status

# See diff
git diff
```

### Stage Files

```bash
# Add all files (respects .gitignore)
git add .

# Add specific files
git add demo/ src/ *.md requirements.txt

# Unstage if needed
git reset HEAD <file>
```

### Commit

```bash
# Commit with message
git commit -m "Initial commit: Complete RMN LoRA System"

# Or use the automated script
./PUSH_TO_GITHUB.sh
```

### Push

```bash
# First push
git push -u origin main

# Subsequent pushes
git push
```

## Common Issues & Solutions

### Issue: Large File Warning

**Error**: `remote: warning: Large files detected`

**Solution**:
```bash
# Find large files
find . -type f -size +50M

# Remove from git
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit
git commit -m "Remove large files"
```

### Issue: Sensitive Data Committed

**Error**: Accidentally committed API key

**Solution**:
```bash
# Remove file from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (dangerous - only if repo is private)
git push --force --all
```

### Issue: Too Many Files

**Error**: `fatal: too many files`

**Solution**:
```bash
# Check file count
git ls-files | wc -l

# Review .gitignore
cat .gitignore

# Add more patterns to .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
```

## Final Checklist

Before running `./PUSH_TO_GITHUB.sh`:

### Code
- [ ] All Python files have proper imports
- [ ] No syntax errors
- [ ] No hardcoded secrets
- [ ] No absolute paths
- [ ] No debug code

### Documentation
- [ ] README is complete
- [ ] Quick start guide works
- [ ] All links are valid
- [ ] Version numbers match

### Configuration
- [ ] .gitignore is comprehensive
- [ ] requirements.txt is complete
- [ ] No .env files staged
- [ ] No config.yaml with secrets

### Testing
- [ ] Main demo launches
- [ ] Admin console launches
- [ ] Data generation works
- [ ] No import errors

### Git
- [ ] Remote is correct (https://github.com/ehiller1/LORA.git)
- [ ] Branch is main
- [ ] No large files staged
- [ ] Commit message is clear

### Security
- [ ] No API keys
- [ ] No passwords
- [ ] No tokens
- [ ] No personal data
- [ ] No client information

## Ready to Push? 🚀

If all checks pass:

```bash
# Option 1: Use automated script (recommended)
./PUSH_TO_GITHUB.sh

# Option 2: Manual push
git add .
git commit -m "Initial commit: Complete RMN LoRA System"
git push -u origin main
```

## After Push

### 1. Verify on GitHub

Visit: https://github.com/ehiller1/LORA

Check:
- [ ] All files uploaded
- [ ] README displays correctly
- [ ] Directory structure is correct
- [ ] No sensitive files visible

### 2. Add Repository Details

On GitHub:
- [ ] Add description
- [ ] Add topics (lora, retail-media, streamlit, ml)
- [ ] Add website (if deployed)
- [ ] Enable issues
- [ ] Add license (if applicable)

### 3. Test Clone

```bash
# In a different directory
cd /tmp
git clone https://github.com/ehiller1/LORA.git
cd LORA
python3 verify_build.py
```

### 4. Create Release (Optional)

```bash
git tag -a v1.0.0 -m "Version 1.0.0 - Initial Release"
git push origin v1.0.0
```

Then create release on GitHub with release notes.

## Summary

✅ **Verification**: Run `python3 verify_build.py`  
✅ **Testing**: Test both UIs locally  
✅ **Security**: No secrets, no large files  
✅ **Documentation**: All guides complete  
✅ **Push**: Run `./PUSH_TO_GITHUB.sh`  

**Repository**: https://github.com/ehiller1/LORA  
**Status**: Ready to push! 🚀
