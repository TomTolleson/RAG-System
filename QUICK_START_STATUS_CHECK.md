# Quick Start: Run Status Check

## 🚀 Quick Way to Run

**Direct Link:** https://github.com/TomTolleson/RAG-System/actions/workflows/status-check.yml

1. Click the link above (or paste it in your browser)
2. Look for **"Run workflow"** button on the **right side** of the page
3. Select branch: `main`
4. Click **"Run workflow"**

## 📍 Where is the Button?

When viewing the workflow page, the "Run workflow" button appears:

```
┌─────────────────────────────────────────┐
│  Repository Status Check                │
│                                         │
│  [Filter workflow runs...]              │
│                                         │
│  Latest workflow runs                   │
│  #3: Fix JSON parsing...   │
│  #2: Manually run by...    │   [Run workflow ▼]
│  #1: Add GitHub status...   │    ↑
│                               │    │
│                               │    └─ Here's the button!
└─────────────────────────────────────────┘
```

## 🔄 Alternative: Via Actions Sidebar

1. Go to: **Actions** tab
2. In **left sidebar**, click **"Repository Status Check"** workflow name
3. The **"Run workflow"** button appears at the top right of that page

## 💡 Tips

- The button is only visible when viewing the **workflow page** (not just the runs list)
- Make sure you're logged in and have write access
- The workflow will run automatically daily at 9 AM UTC

## 📞 Still Can't Find It?

If you don't see the button:
1. Make sure you're viewing: `https://github.com/TomTolleson/RAG-System/actions/workflows/status-check.yml`
2. Check you have write permissions to the repo
3. Try refreshing the page

---

**Note:** The workflow also runs automatically:
- ✅ Daily at 9:00 AM UTC
- ✅ When you push changes to the workflow file
- ✅ When you push changes to `check_github_status.py`

