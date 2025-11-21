# Git Setup Guide - Multiple Remotes

Since this package uses a symbolic link, there's only one git repository that can push to multiple remotes.

## Option 1: Multiple Remotes in One Repository (Recommended)

### Initial Setup

```bash
cd /Users/jsjukara/git/private_repo/llm-context-processor

# Initialize git if not already done
git init

# Add GitLab remote (your private/work repository)
git remote add gitlab YOUR_GITLAB_URL

# Add GitHub remote (public repository)
git remote add github YOUR_GITHUB_URL

# View all remotes
git remote -v
```

### Push to Both Remotes

```bash
# Push to GitLab
git push gitlab main

# Push to GitHub
git push github main

# Or push to both at once
git push gitlab main && git push github main
```

### Set Default Remote

```bash
# Set GitLab as default
git branch --set-upstream-to=gitlab/main main

# Then you can just use
git push  # pushes to GitLab (default)
git push github main  # explicitly push to GitHub
```

## Option 2: Remove Symlink and Use Git Worktrees

If you really need separate git repositories, use git worktrees:

```bash
cd /Users/jsjukara/git/private_repo/llm-context-processor

# Initialize main repo (for GitLab)
git init
git remote add origin YOUR_GITLAB_URL

# Create a worktree for GitHub in git-personal
git worktree add /Users/jsjukara/git-personal/llm-context-processor main

# Now you have:
# - /Users/jsjukara/git/private_repo/llm-context-processor -> connected to GitLab
# - /Users/jsjukara/git-personal/llm-context-processor -> same repo, different working directory
```

## Option 3: Keep Symlink, Use Push URLs

Add both remotes to a single "origin":

```bash
cd /Users/jsjukara/git/private_repo/llm-context-processor

git init
git remote add origin YOUR_GITLAB_URL
git remote set-url --add --push origin YOUR_GITLAB_URL
git remote set-url --add --push origin YOUR_GITHUB_URL

# Now "git push" will push to BOTH remotes at once
git push origin main  # pushes to both GitLab and GitHub
```

## Recommendation

**Use Option 1** (Multiple Remotes) because:
- Simple and clear
- Easy to control which remote to push to
- Works perfectly with the symlink setup
- You can have different content/branches on each remote if needed

## Current Status

- ✅ Symlink created: `/Users/jsjukara/git-personal/llm-context-processor` → `/Users/jsjukara/git/private_repo/llm-context-processor`
- ✅ Single source of truth for code
- ✅ Edit in either location, changes are synchronized
- 🔄 Git repository not yet initialized (waiting for your preferred setup)
