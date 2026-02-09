# Renaming GitHub and Vercel Repositories

⚠️ **IMPORTANT**: The rename procedure described below does not work reliably. **Delete everything and start over** instead.

## Problem

When you accept Vercel's default name suggestion during project creation, you might end up with a repository name like `bizcad-blog-starter-kitf` when you intended it to be something like `roadtrip-blog`. Attempting to rename the repositories after creation leads to persistent connection issues between GitHub and Vercel.

## Why Renaming Doesn't Work

Renaming the repositories after initial creation causes:
- Vercel failing to properly reconnect to the renamed GitHub repository
- Broken deployment pipelines
- Confusion with environment variables and settings
- Difficulty in maintaining the correct repository link

**The most reliable solution is to delete everything and start fresh.**

## Recommended Solution: Delete and Recreate

### Step 1: Delete the Vercel Project

1. Go to your Vercel dashboard
2. Select the project with the incorrect name
3. Navigate to **Settings** → **General**
4. Scroll to the bottom and click **Delete Project**
5. Confirm the deletion

### Step 2: Delete the GitHub Repository

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/INCORRECT_REPO_NAME`
2. Click **Settings** (top right of the repository)
3. Scroll to the bottom and find **Danger Zone** section
4. Click **Delete this repository**
5. Confirm by entering the repository name

### Step 3: Delete the Local Folder

Delete the local folder from your machine (e.g., `G:\repos\AI\YOUR_INCORRECT_PROJECT_NAME`)

### Step 4: Create Fresh from Vercel

1. Go to [Vercel](https://vercel.com)
2. Click **Add New** → **Project**
3. Select **Import Git Repository** and choose the blog starter template
4. **Specify the correct repository name** (e.g., `roadtrip-blog`) during project creation
5. Complete the setup; Vercel will create both the GitHub repository and the Vercel project with the correct configuration

This approach ensures:
- Correct repository naming from the start
- Proper GitHub-to-Vercel connection
- Clean environment variables and settings
- No orphaned or misconfigured resources

## References

- [Vercel: Project Settings](https://vercel.com/docs/projects/overview)
- [GitHub: Deleting a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/deleting-a-repository)
