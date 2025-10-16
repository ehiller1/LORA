#!/bin/bash

# Push to GitHub Script for RMN LoRA System
# Repository: https://github.com/ehiller1/LORA

set -e

echo "🚀 RMN LoRA System - GitHub Push Script"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "verify_build.py" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Run verification
echo "📋 Step 1: Running verification checks..."
python3 verify_build.py
verification_status=$?

if [ $verification_status -ne 0 ]; then
    echo ""
    echo "⚠️  Verification found issues, but we can still push to GitHub"
    echo "   (Dependencies are not required for the repository)"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check git status
echo ""
echo "📊 Step 2: Checking git status..."
if [ ! -d ".git" ]; then
    echo "   Initializing git repository..."
    git init
    echo "   ✅ Git initialized"
else
    echo "   ✅ Git repository exists"
fi

# Check remote
echo ""
echo "🔗 Step 3: Checking remote repository..."
if git remote | grep -q "origin"; then
    current_remote=$(git remote get-url origin)
    echo "   Current remote: $current_remote"
    
    if [ "$current_remote" != "https://github.com/ehiller1/LORA.git" ]; then
        echo "   ⚠️  Remote URL doesn't match expected repository"
        read -p "Update remote to https://github.com/ehiller1/LORA.git? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote set-url origin https://github.com/ehiller1/LORA.git
            echo "   ✅ Remote updated"
        fi
    else
        echo "   ✅ Remote configured correctly"
    fi
else
    echo "   Adding remote repository..."
    git remote add origin https://github.com/ehiller1/LORA.git
    echo "   ✅ Remote added"
fi

# Show what will be committed
echo ""
echo "📁 Step 4: Files to be committed..."
echo ""
git add -n . | head -20
file_count=$(git add -n . | wc -l)
echo "   ... and $file_count total files"
echo ""

read -p "Review files and continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Stage files
echo ""
echo "📦 Step 5: Staging files..."
git add .
echo "   ✅ Files staged"

# Show status
echo ""
echo "📊 Git status:"
git status --short | head -20
echo ""

# Commit
echo ""
echo "💾 Step 6: Creating commit..."
echo ""
echo "Commit message:"
echo "==============="
cat << 'EOF'
Initial commit: Complete RMN LoRA System

Features:
- 4 functional UIs (Main Demo, Admin Console, RLHF, NDE Rater)
- 7 production agents (data harmonization, planning, optimization, etc.)
- Complete LoRA training pipeline (SFT/DPO/QLoRA)
- Multi-tenant runtime with adapter federation
- 63+ pages of comprehensive documentation
- Synthetic data generator (18K events, 100 SKUs)
- Professional CSS styling with Archivo font
- Real tools: DuckDB warehouse, PuLP optimizer, policy checker
- Demo scripts and quick start guides

Technical Stack:
- Python 3.8+
- Streamlit for UIs
- DuckDB for data warehouse
- PuLP for optimization
- SQLAlchemy for persistence
- PEFT/LoRA for model adaptation

Documentation:
- Complete architecture guides
- User manuals for all UIs
- Demo scripts (15-minute presentation)
- API documentation
- Training guides

Ready to run:
1. pip install -r requirements.txt
2. cd demo && python generate_synthetic_data.py
3. streamlit run streamlit_app.py
EOF
echo "==============="
echo ""

read -p "Proceed with this commit message? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Enter custom commit message (or press Ctrl+C to abort):"
    read -r custom_message
    git commit -m "$custom_message"
else
    git commit -F - << 'EOF'
Initial commit: Complete RMN LoRA System

Features:
- 4 functional UIs (Main Demo, Admin Console, RLHF, NDE Rater)
- 7 production agents (data harmonization, planning, optimization, etc.)
- Complete LoRA training pipeline (SFT/DPO/QLoRA)
- Multi-tenant runtime with adapter federation
- 63+ pages of comprehensive documentation
- Synthetic data generator (18K events, 100 SKUs)
- Professional CSS styling with Archivo font
- Real tools: DuckDB warehouse, PuLP optimizer, policy checker
- Demo scripts and quick start guides

Technical Stack:
- Python 3.8+
- Streamlit for UIs
- DuckDB for data warehouse
- PuLP for optimization
- SQLAlchemy for persistence
- PEFT/LoRA for model adaptation

Documentation:
- Complete architecture guides
- User manuals for all UIs
- Demo scripts (15-minute presentation)
- API documentation
- Training guides

Ready to run:
1. pip install -r requirements.txt
2. cd demo && python generate_synthetic_data.py
3. streamlit run streamlit_app.py
EOF
fi

echo "   ✅ Commit created"

# Check branch
echo ""
echo "🌿 Step 7: Checking branch..."
current_branch=$(git branch --show-current)
if [ -z "$current_branch" ]; then
    echo "   Creating main branch..."
    git branch -M main
    echo "   ✅ Main branch created"
else
    echo "   Current branch: $current_branch"
    if [ "$current_branch" != "main" ]; then
        read -p "Switch to main branch? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git branch -M main
            echo "   ✅ Switched to main"
        fi
    else
        echo "   ✅ On main branch"
    fi
fi

# Push
echo ""
echo "🚀 Step 8: Pushing to GitHub..."
echo ""
echo "⚠️  You may be prompted for GitHub credentials"
echo "   Username: ehiller1"
echo "   Password: <your-personal-access-token>"
echo ""

read -p "Ready to push? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted. Commit is saved locally."
    echo "To push later, run: git push -u origin main"
    exit 1
fi

echo ""
echo "Pushing to https://github.com/ehiller1/LORA.git..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Successfully pushed to GitHub!"
    echo "========================================"
    echo ""
    echo "🎉 Your repository is now live at:"
    echo "   https://github.com/ehiller1/LORA"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Visit the repository and verify files"
    echo "   2. Add repository description and topics"
    echo "   3. Create a release (optional)"
    echo "   4. Share with your team!"
    echo ""
    echo "📖 For clone instructions, see:"
    echo "   https://github.com/ehiller1/LORA#quick-start"
    echo ""
else
    echo ""
    echo "========================================"
    echo "❌ Push failed"
    echo "========================================"
    echo ""
    echo "Common issues:"
    echo "   1. Authentication failed"
    echo "      → Use personal access token as password"
    echo "      → GitHub → Settings → Developer settings → Tokens"
    echo ""
    echo "   2. Remote repository doesn't exist"
    echo "      → Create repository on GitHub first"
    echo "      → https://github.com/new"
    echo ""
    echo "   3. Branch protection rules"
    echo "      → Check repository settings"
    echo ""
    echo "To retry: git push -u origin main"
    exit 1
fi
