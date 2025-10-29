# GitHub Status Checker

A command-line tool to check your GitHub repository status without opening the browser.

## Features

- ✅ Check Dependabot security alerts
- ✅ View CI/CD workflow status
- ✅ Repository health metrics
- ✅ Overall health score

## Setup

1. **Create a GitHub Personal Access Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Give it a name (e.g., "Status Checker")
   - Select scopes: `repo` and `security_events`
   - Copy the token

2. **Set the token as an environment variable:**
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```
   
   Or add it to your `.env` file:
   ```bash
   echo "GITHUB_TOKEN=your_token_here" >> .env
   ```

3. **Run the checker:**
   ```bash
   python check_github_status.py
   ```

## Usage

### Basic Usage
```bash
# Auto-detect repository from git remote
python check_github_status.py
```

### Specify Repository
```bash
python check_github_status.py --repo owner/repo-name
```

### Use Different Token
```bash
python check_github_status.py --token your_token_here
```

### JSON Output
```bash
python check_github_status.py --json
```

## Example Output

```
======================================================================
GitHub Repository Status: TomTolleson/RAG-System
======================================================================

📦 DEPENDABOT ALERTS
----------------------------------------------------------------------
✅ No open security alerts found!

🔄 CI/CD WORKFLOW STATUS
----------------------------------------------------------------------
✅ Latest: CI (success)
   Run #42 - 2024-01-15T10:30:00Z
   https://github.com/TomTolleson/RAG-System/actions/runs/123456

📊 REPOSITORY INFO
----------------------------------------------------------------------
🌟 Stars: 5
🍴 Forks: 2
📝 Open Issues: 0
🔒 Visibility: public
🔗 URL: https://github.com/TomTolleson/RAG-System

======================================================================
📈 OVERALL HEALTH SCORE
----------------------------------------------------------------------
✅ EXCELLENT - Score: 100/100

✅ No critical issues found!

======================================================================
Report generated at: 2024-01-15 10:35:00
======================================================================
```

## Troubleshooting

### Authentication Errors
- Make sure your token has the `repo` and `security_events` scopes
- Check that the token hasn't expired
- Verify the repository name is correct (owner/repo format)

### Rate Limiting
GitHub API has rate limits:
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

The script will show remaining requests when hitting limits.

### No Dependabot Alerts Shown
- Make sure Dependabot is enabled for your repository
- Ensure your token has `security_events` scope
- Some alerts may require repository admin access

## Integration

You can integrate this into your workflow:

### Add to `.gitignore` or make executable:
```bash
chmod +x check_github_status.py
```

### Create an alias in your shell:
```bash
# Add to ~/.zshrc or ~/.bashrc
alias gh-status="cd /path/to/RAG-System && python check_github_status.py"
```

### Run in CI/CD:
You can call this script from GitHub Actions to monitor status automatically.

