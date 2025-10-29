#!/bin/bash
# Quick status check script

echo "🔍 Checking GitHub repository status..."
echo ""

# Check if we have a GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  No GITHUB_TOKEN found in environment."
    echo "   Set it with: export GITHUB_TOKEN=your_token_here"
    echo "   Or create one at: https://github.com/settings/tokens"
    echo ""
fi

# Run the status checker
python check_github_status.py

