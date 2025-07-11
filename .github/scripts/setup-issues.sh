#!/bin/bash

# Script to create all GitHub issues from templates
# Usage: ./setup-issues.sh [--dry-run]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if this is a dry run
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}Running in dry-run mode. No issues will be created.${NC}"
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is not installed. Please install it first.${NC}"
    echo "Visit: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Not in a git repository. Please run from the project root.${NC}"
    exit 1
fi

# Function to create an issue
create_issue() {
    local file=$1
    local type=$2
    local title=$(grep -m1 "^# " "$file" | sed 's/# //')
    
    echo -e "${GREEN}Creating $type: $title${NC}"
    
    if [[ "$DRY_RUN" == false ]]; then
        # Extract labels from the file
        labels=$(grep "Labels:" "$file" | sed 's/.*Labels: //' | sed 's/`//g' | tr ' ' '\n' | grep -v '^$' | paste -sd, -)
        
        # Create the issue
        gh issue create \
            --title "$title" \
            --body-file "$file" \
            --label "$labels" \
            --milestone "v1.0 - Foundation"
    else
        echo "  Would create with labels: $(grep "Labels:" "$file" | sed 's/.*Labels: //')"
    fi
}

# Create labels first
echo -e "${YELLOW}Setting up labels...${NC}"
if [[ "$DRY_RUN" == false ]]; then
    # Read labels.yml and create each label
    while IFS= read -r line; do
        if [[ $line =~ ^-\ name:\ \"(.*)\" ]]; then
            name="${BASH_REMATCH[1]}"
        elif [[ $line =~ ^\ \ color:\ \"(.*)\" ]]; then
            color="${BASH_REMATCH[1]}"
        elif [[ $line =~ ^\ \ description:\ \"(.*)\" ]]; then
            description="${BASH_REMATCH[1]}"
            
            echo "Creating label: $name"
            gh label create "$name" --color "$color" --description "$description" --force || true
        fi
    done < .github/labels.yml
fi

# Create milestones
echo -e "${YELLOW}Setting up milestones...${NC}"
if [[ "$DRY_RUN" == false ]]; then
    gh api repos/:owner/:repo/milestones \
        --method POST \
        --field title="v1.0 - Foundation" \
        --field description="Production-ready infrastructure" \
        --field due_on="2024-03-31T23:59:59Z" || true
        
    gh api repos/:owner/:repo/milestones \
        --method POST \
        --field title="v1.1 - API Excellence" \
        --field description="Feature-complete API" \
        --field due_on="2024-05-15T23:59:59Z" || true
fi

# Create Epics
echo -e "${YELLOW}Creating Epic issues...${NC}"
for file in .github/ISSUES/EPIC-*.md; do
    if [[ -f "$file" ]]; then
        create_issue "$file" "Epic"
    fi
done

# Create Features
echo -e "${YELLOW}Creating Feature issues...${NC}"
for file in .github/ISSUES/FEATURE-*.md; do
    if [[ -f "$file" ]]; then
        create_issue "$file" "Feature"
    fi
done

echo -e "${GREEN}✅ Issue setup complete!${NC}"

# Show summary
if [[ "$DRY_RUN" == false ]]; then
    echo -e "${YELLOW}Summary:${NC}"
    echo "Total issues: $(gh issue list --limit 1000 | wc -l)"
    echo "Open epics: $(gh issue list --label epic | wc -l)"
    echo "Open features: $(gh issue list --label feature | wc -l)"
else
    echo -e "${YELLOW}This was a dry run. Run without --dry-run to create issues.${NC}"
fi