#!/usr/bin/env python3
"""
GitHub Repository Status Checker

This script checks:
- Dependabot alerts and security vulnerabilities
- CI/CD workflow status
- Repository health
- Overall status summary

Usage:
    python check_github_status.py
    python check_github_status.py --repo owner/repo
    python check_github_status.py --token YOUR_GITHUB_TOKEN
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


@dataclass
class Alert:
    """Represents a security alert."""
    number: int
    severity: str
    state: str
    dependency: str
    description: str
    url: str
    created_at: str


@dataclass
class WorkflowRun:
    """Represents a workflow run."""
    name: str
    status: str
    conclusion: str
    run_number: int
    created_at: str
    html_url: str


class GitHubStatusChecker:
    """Check GitHub repository status using the GitHub API."""
    
    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo = repo or self._get_repo_from_git()
        
        if not self.token:
            print("Warning: No GitHub token found.")
            print("Set GITHUB_TOKEN environment variable or use --token flag.")
            print("You can create a token at: https://github.com/settings/tokens")
            print("Required scopes: repo, security_events")
            print()
        
        if not self.repo:
            print("Error: Could not determine repository.")
            print("Set --repo owner/repo or run from a git repository.")
            sys.exit(1)
        
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def _get_repo_from_git(self) -> Optional[str]:
        """Try to get repository from git config."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            url = result.stdout.strip()
            
            # Extract owner/repo from git URL
            if "github.com" in url:
                # Format: https://github.com/owner/repo.git or git@github.com:owner/repo.git
                parts = url.replace("https://", "").replace("http://", "").replace("git@", "")
                parts = parts.replace("github.com:", "").replace("github.com/", "")
                parts = parts.replace(".git", "").strip()
                if "/" in parts:
                    return "/".join(parts.split("/")[-2:])
        except Exception:
            pass
        return None
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the GitHub API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 401:
                print("Error: Authentication failed. Check your GitHub token.")
                sys.exit(1)
            elif response.status_code == 404:
                print(f"Error: Repository '{self.repo}' not found or access denied.")
                sys.exit(1)
            elif response.status_code == 403:
                print("Error: API rate limit exceeded or insufficient permissions.")
                if "x-ratelimit-remaining" in response.headers:
                    remaining = response.headers.get("x-ratelimit-remaining", "?")
                    reset_time = response.headers.get("x-ratelimit-reset", "?")
                    print(f"Rate limit remaining: {remaining}")
                sys.exit(1)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to GitHub API: {e}")
            sys.exit(1)
    
    def check_dependabot_alerts(self) -> List[Alert]:
        """Check for Dependabot security alerts."""
        print("📦 Checking Dependabot alerts...")
        
        alerts = []
        endpoint = f"repos/{self.repo}/dependabot/alerts"
        params = {"state": "open", "per_page": 100}
        
        try:
            data = self._make_request(endpoint, params)
            
            for alert in data:
                alerts.append(Alert(
                    number=alert.get("number", 0),
                    severity=alert.get("security_advisory", {}).get("severity", "unknown").upper(),
                    state=alert.get("state", "unknown"),
                    dependency=alert.get("dependency", {}).get("package", {}).get("name", "unknown"),
                    description=alert.get("security_advisory", {}).get("summary", "No description"),
                    url=alert.get("html_url", ""),
                    created_at=alert.get("created_at", "")
                ))
        except Exception as e:
            print(f"   ⚠️  Could not fetch Dependabot alerts: {e}")
            print("   (This might require a token with 'security_events' scope)")
        
        return alerts
    
    def check_workflow_runs(self, limit: int = 5) -> List[WorkflowRun]:
        """Check recent workflow runs."""
        print("🔄 Checking CI/CD workflow status...")
        
        runs = []
        endpoint = f"repos/{self.repo}/actions/runs"
        params = {"per_page": limit}
        
        try:
            data = self._make_request(endpoint, params)
            
            for run in data.get("workflow_runs", []):
                runs.append(WorkflowRun(
                    name=run.get("name", "Unknown"),
                    status=run.get("status", "unknown"),
                    conclusion=run.get("conclusion", "unknown"),
                    run_number=run.get("run_number", 0),
                    created_at=run.get("created_at", ""),
                    html_url=run.get("html_url", "")
                ))
        except Exception as e:
            print(f"   ⚠️  Could not fetch workflow runs: {e}")
        
        return runs
    
    def check_repository_status(self) -> Dict:
        """Check general repository status."""
        print("📊 Checking repository status...")
        
        endpoint = f"repos/{self.repo}"
        try:
            return self._make_request(endpoint)
        except Exception as e:
            print(f"   ⚠️  Could not fetch repository info: {e}")
            return {}
    
    def print_summary(self, alerts: List[Alert], workflows: List[WorkflowRun], repo_info: Dict):
        """Print a formatted summary of all checks."""
        print("\n" + "=" * 70)
        print(f"GitHub Repository Status: {self.repo}")
        print("=" * 70)
        
        # Dependabot Alerts
        print("\n📦 DEPENDABOT ALERTS")
        print("-" * 70)
        if not alerts:
            print("✅ No open security alerts found!")
        else:
            by_severity = {}
            for alert in alerts:
                by_severity.setdefault(alert.severity, []).append(alert)
            
            for severity in ["CRITICAL", "HIGH", "MODERATE", "LOW"]:
                if severity in by_severity:
                    count = len(by_severity[severity])
                    icon = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡" if severity == "MODERATE" else "🔵"
                    print(f"{icon} {severity}: {count} alert(s)")
            
            print(f"\n⚠️  Total open alerts: {len(alerts)}")
            print("\nTop 5 alerts:")
            for alert in sorted(alerts, key=lambda x: (x.severity == "CRITICAL", x.severity == "HIGH"), reverse=True)[:5]:
                print(f"  • [{alert.severity}] {alert.dependency}")
                print(f"    {alert.description[:60]}...")
                print(f"    {alert.url}")
        
        # Workflow Status
        print("\n🔄 CI/CD WORKFLOW STATUS")
        print("-" * 70)
        if not workflows:
            print("⚠️  No recent workflow runs found")
        else:
            latest = workflows[0]
            status_icon = {
                "success": "✅",
                "failure": "❌",
                "cancelled": "⚠️",
                "in_progress": "🔄",
                "queued": "⏳"
            }.get(latest.conclusion or latest.status, "❓")
            
            print(f"{status_icon} Latest: {latest.name} ({latest.conclusion or latest.status})")
            print(f"   Run #{latest.run_number} - {latest.created_at}")
            print(f"   {latest.html_url}")
            
            if len(workflows) > 1:
                print(f"\nRecent runs ({len(workflows)} shown):")
                for run in workflows[:5]:
                    icon = status_icon.get(run.conclusion or run.status, "❓")
                    print(f"  {icon} {run.name} - {run.conclusion or run.status}")
        
        # Repository Info
        if repo_info:
            print("\n📊 REPOSITORY INFO")
            print("-" * 70)
            print(f"🌟 Stars: {repo_info.get('stargazers_count', 0)}")
            print(f"🍴 Forks: {repo_info.get('forks_count', 0)}")
            print(f"📝 Open Issues: {repo_info.get('open_issues_count', 0)}")
            print(f"🔒 Visibility: {repo_info.get('visibility', 'unknown')}")
            print(f"🔗 URL: {repo_info.get('html_url', '')}")
        
        # Overall Health Score
        print("\n" + "=" * 70)
        print("📈 OVERALL HEALTH SCORE")
        print("-" * 70)
        
        score = 100
        issues = []
        
        critical_alerts = sum(1 for a in alerts if a.severity == "CRITICAL")
        high_alerts = sum(1 for a in alerts if a.severity == "HIGH")
        
        if critical_alerts > 0:
            score -= 30
            issues.append(f"{critical_alerts} critical security alert(s)")
        if high_alerts > 0:
            score -= 15
            issues.append(f"{high_alerts} high severity alert(s)")
        if len(alerts) > 10:
            score -= 10
            issues.append("Many open security alerts")
        
        failed_workflows = [w for w in workflows if w.conclusion == "failure"]
        if failed_workflows:
            score -= 20
            issues.append(f"{len(failed_workflows)} failed workflow(s)")
        
        if score >= 90:
            status = "✅ EXCELLENT"
        elif score >= 75:
            status = "🟡 GOOD"
        elif score >= 60:
            status = "🟠 NEEDS ATTENTION"
        else:
            status = "🔴 CRITICAL"
        
        print(f"{status} - Score: {score}/100")
        
        if issues:
            print("\n⚠️  Issues to address:")
            for issue in issues:
                print(f"  • {issue}")
        else:
            print("\n✅ No critical issues found!")
        
        print("\n" + "=" * 70)
        print(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Check GitHub repository status including Dependabot alerts and CI/CD workflows"
    )
    parser.add_argument(
        "--repo",
        help="Repository in format owner/repo (default: auto-detect from git)",
        default=None
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token (default: GITHUB_TOKEN env var)",
        default=None
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    checker = GitHubStatusChecker(token=args.token, repo=args.repo)
    
    alerts = checker.check_dependabot_alerts()
    workflows = checker.check_workflow_runs()
    repo_info = checker.check_repository_status()
    
    if args.json:
        try:
            output = {
                "repository": checker.repo,
                "timestamp": datetime.now().isoformat(),
                "alerts": [
                    {
                        "number": a.number,
                        "severity": a.severity,
                        "state": a.state,
                        "dependency": a.dependency,
                        "description": a.description,
                        "url": a.url,
                        "created_at": a.created_at
                    }
                    for a in alerts
                ],
                "workflows": [
                    {
                        "name": w.name,
                        "status": w.status,
                        "conclusion": w.conclusion,
                        "run_number": w.run_number,
                        "created_at": w.created_at,
                        "url": w.html_url
                    }
                    for w in workflows
                ],
                "repository_info": repo_info
            }
            # Print JSON to stdout only, errors go to stderr
            print(json.dumps(output, indent=2))
        except Exception as e:
            # Ensure we always output valid JSON even on error
            error_output = {
                "repository": checker.repo,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "alerts": [],
                "workflows": [],
                "repository_info": {}
            }
            print(json.dumps(error_output, indent=2))
            sys.stderr.write(f"Error generating report: {e}\n")
            sys.exit(1)
    else:
        checker.print_summary(alerts, workflows, repo_info)


if __name__ == "__main__":
    main()

