#!/bin/bash

# Script to update download links in Vedabase website (gh-pages)
# Usage: ./update-download-links.sh 1.4.3

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if version is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Version number required${NC}"
    echo "Usage: ./update-download-links.sh 1.4.3"
    exit 1
fi

NEW_VERSION="$1"
REPO_URL="https://github.com/juanmanuelferrera/vedabase-app"

echo -e "${YELLOW}Updating download links to version ${NEW_VERSION}...${NC}"

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH=$(git rev-parse HEAD)
fi
echo -e "Current branch: ${CURRENT_BRANCH}"

# Stash any uncommitted changes
echo -e "${YELLOW}Stashing any uncommitted changes...${NC}"
git stash push -m "Pre-download-link-update stash"

# Checkout gh-pages
echo -e "${YELLOW}Checking out gh-pages branch...${NC}"
git checkout gh-pages

# Update download links in all HTML files
echo -e "${YELLOW}Updating download links...${NC}"

# Files to update
FILES=(
    "index.html"
    "docs/index.html"
    "docs/vedabase.html"
)

for FILE in "${FILES[@]}"; do
    if [ -f "$FILE" ]; then
        echo -e "  Updating ${FILE}..."

        # Update Windows download link
        sed -i '' -E "s|${REPO_URL}/releases/download/v[0-9]+\.[0-9]+\.[0-9]+/Vedabase_[0-9]+\.[0-9]+\.[0-9]+_x64-setup\.exe|${REPO_URL}/releases/download/v${NEW_VERSION}/Vedabase_${NEW_VERSION}_x64-setup.exe|g" "$FILE"

        # Update macOS download link
        sed -i '' -E "s|${REPO_URL}/releases/download/v[0-9]+\.[0-9]+\.[0-9]+/Vedabase_[0-9]+\.[0-9]+\.[0-9]+_aarch64\.dmg|${REPO_URL}/releases/download/v${NEW_VERSION}/Vedabase_${NEW_VERSION}_aarch64.dmg|g" "$FILE"

        # Update Linux download link
        sed -i '' -E "s|${REPO_URL}/releases/download/v[0-9]+\.[0-9]+\.[0-9]+/Vedabase_[0-9]+\.[0-9]+\.[0-9]+_amd64\.deb|${REPO_URL}/releases/download/v${NEW_VERSION}/Vedabase_${NEW_VERSION}_amd64.deb|g" "$FILE"

        # Update version display text (e.g., "Version 1.4.2" -> "Version 1.4.3")
        sed -i '' -E "s|Version [0-9]+\.[0-9]+\.[0-9]+|Version ${NEW_VERSION}|g" "$FILE"
    else
        echo -e "  ${RED}Warning: ${FILE} not found${NC}"
    fi
done

# Show changes
echo -e "${YELLOW}Changes made:${NC}"
git diff

# Confirm before committing
echo -e "${YELLOW}Do you want to commit and push these changes? (y/n)${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo -e "${RED}Aborted. Returning to ${CURRENT_BRANCH}...${NC}"
    git checkout "$CURRENT_BRANCH"
    git stash pop || true
    exit 1
fi

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git add "${FILES[@]}"
git commit -m "Update download links to v${NEW_VERSION}

- Windows: Vedabase_${NEW_VERSION}_x64-setup.exe
- macOS: Vedabase_${NEW_VERSION}_aarch64.dmg
- Linux: Vedabase_${NEW_VERSION}_amd64.deb
- Updated version displays to ${NEW_VERSION}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to gh-pages
echo -e "${YELLOW}Pushing to gh-pages...${NC}"
git push origin gh-pages

# Return to original branch
echo -e "${YELLOW}Returning to ${CURRENT_BRANCH}...${NC}"
git checkout "$CURRENT_BRANCH"

# Restore stashed changes
echo -e "${YELLOW}Restoring stashed changes...${NC}"
git stash pop || echo -e "${YELLOW}No stashed changes to restore${NC}"

echo -e "${GREEN}✅ Download links updated successfully!${NC}"
echo -e "${GREEN}Website will be live at: https://juanmanuelferrera.github.io/vedabase-app/${NC}"
echo -e "${GREEN}Changes may take a few minutes to appear.${NC}"
