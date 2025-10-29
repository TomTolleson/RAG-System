#!/bin/bash
# Simple script to trigger the status check workflow via GitHub CLI

echo "🔍 Triggering Repository Status Check workflow..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "Install it with:"
    echo "  macOS: brew install gh"
    echo "  Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo ""
    echo "Then authenticate: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

# Trigger the workflow
echo "🚀 Running workflow..."
gh workflow run "Repository Status Check"

if [ $? -eq 0 ]; then
    echo "✅ Workflow triggered successfully!"
    echo "View it at: https://github.com/TomTolleson/RAG-System/actions"
else
    echo "❌ Failed to trigger workflow. Check your permissions."
    exit 1
fi
