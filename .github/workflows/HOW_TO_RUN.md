# How to Manually Run the Status Check Workflow

## Step-by-Step Instructions

1. **Go to the Actions tab** in your GitHub repository
   - Navigate to: `https://github.com/TomTolleson/RAG-System/actions`

2. **Click on the workflow name** in the left sidebar
   - Look for **"Repository Status Check"** or **".github/workflows/status-check.yml"**
   - This is important - you need to click on the workflow name, not just view the runs

3. **Find the "Run workflow" button**
   - Once you're on the workflow page, look at the **top right** of the page
   - You should see a blue **"Run workflow"** dropdown button
   - It will be next to the workflow runs list

4. **Click "Run workflow"**
   - Click the button
   - Select the branch (usually `main`)
   - Click the green **"Run workflow"** button

## Visual Guide

```
Actions Tab → [Click "Repository Status Check" in left sidebar] → [Top right: "Run workflow" button]
```

## Alternative Method

If you don't see the button:

1. Make sure you're on the main Actions page
2. In the left sidebar, click on **".github/workflows/status-check.yml"**
3. The "Run workflow" button should appear in the top right corner

## Troubleshooting

### No "Run workflow" button?
- Make sure you have **write permissions** to the repository
- Refresh the page
- Try navigating directly to: `https://github.com/TomTolleson/RAG-System/actions/workflows/status-check.yml`

### Button is grayed out?
- Check that the workflow file is on the default branch (main)
- Ensure `workflow_dispatch` is in the workflow file (it should be)

## Quick Link

Direct link to the workflow page:
`https://github.com/TomTolleson/RAG-System/actions/workflows/status-check.yml`

