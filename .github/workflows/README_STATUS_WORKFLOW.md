# Repository Status Check Workflow

This GitHub Actions workflow automatically monitors your repository's health and reports issues.

## What It Does

- **Runs Daily**: Checks status every day at 9:00 AM UTC
- **Manual Trigger**: Can be run manually from the Actions tab
- **Auto-Detection**: Automatically detects critical issues

## Features

### 1. Status Monitoring
- Checks Dependabot security alerts
- Monitors CI/CD workflow status
- Tracks repository health metrics

### 2. Automatic Issue Creation
- Creates GitHub issues when critical problems are detected
- Updates existing issues with new reports
- Labels issues with `status-check-critical` for easy filtering

### 3. PR Comments
- Automatically comments on pull requests with status summary
- Shows security alert counts
- Displays latest CI/CD status

### 4. Artifact Storage
- Saves full status report as JSON artifact
- Retains reports for 7 days
- Downloadable from workflow runs

## Workflow Triggers

The workflow runs on:
1. **Schedule**: Daily at 9:00 AM UTC (via cron)
2. **Manual**: Click "Run workflow" in GitHub Actions tab
3. **Push**: When status check files are updated

## Viewing Results

### In GitHub Actions
1. Go to the "Actions" tab in your repository
2. Click on "Repository Status Check" workflow
3. View the latest run summary

### Status Report Artifact
1. Open any workflow run
2. Scroll to "Artifacts" section
3. Download `status-report` to get the full JSON report

### Issues
- Check the Issues tab
- Filter by label: `status-check-critical`
- Look for automated issues with status updates

## Customization

### Change Schedule
Edit `.github/workflows/status-check.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'  # Change time/date pattern
```

Cron format: `minute hour day-of-month month day-of-week`

Examples:
- `0 9 * * *` - 9 AM UTC daily
- `0 0 * * 1` - Monday at midnight UTC
- `0 */6 * * *` - Every 6 hours

### Alert Thresholds
The workflow currently creates issues for:
- Critical security alerts (> 0)
- Failed workflows (> 0)

To adjust thresholds, edit the condition:
```yaml
if: steps.parse_status.outputs.critical_alerts > '0'
```

### Disable Auto-Issue Creation
Remove or comment out the "Create issue for critical problems" step in the workflow file.

## Permissions

The workflow requires:
- `contents: read` - Read repository content
- `issues: write` - Create/update issues
- `pull-requests: write` - Comment on PRs
- `security-events: read` - Read Dependabot alerts

These are automatically available via `secrets.GITHUB_TOKEN` in GitHub Actions.

## Troubleshooting

### Workflow Fails to Run
- Check that `check_github_status.py` exists in repository root
- Verify Python dependencies are installed correctly
- Review workflow logs for specific errors

### No Security Alerts Shown
- Ensure Dependabot is enabled in repository settings
- Verify repository has security features enabled
- Check that `security-events: read` permission is granted

### Issues Not Created
- Verify workflow has `issues: write` permission
- Check if issue with same label already exists (it updates instead)
- Review GitHub Actions logs for API errors

## Integration Tips

### Slack/Discord Notifications
Add a step to send notifications:
```yaml
- name: Notify Slack
  if: steps.parse_status.outputs.critical_alerts > '0'
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "🔴 Critical issues detected in repository!"
      }
```

### Email Notifications
GitHub automatically sends email notifications for failed workflows if configured in your account settings.

