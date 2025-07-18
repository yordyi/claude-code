# Scripts Directory

This directory contains utility scripts for the Claude Code project.

## analyze_commits.py

A Git commit analysis tool that analyzes recent commits and provides insights about commit patterns, authors, changes, and activity.

### Features

- Analyzes recent commits with detailed statistics
- Provides author contribution analysis
- Shows file change frequency
- Supports both human-readable text and JSON output formats
- Customizable number of commits to analyze

### Usage

```bash
# Analyze last 10 commits (default)
python3 Script/analyze_commits.py

# Analyze last 20 commits
python3 Script/analyze_commits.py --count 20

# Get JSON output for integration with other tools
python3 Script/analyze_commits.py --output json

# Get help
python3 Script/analyze_commits.py --help
```

### Output

The tool provides:

- **Summary**: Total commits, time span, line changes, average files per commit
- **Author Analysis**: Commits per author, lines changed, unique files touched
- **Recent Commits**: List of recent commits with metadata
- **File Analysis**: Most frequently changed files

### Example Output

```
📊 Git Commit Analysis Report
========================================

📈 Summary:
  • Total commits analyzed: 2
  • Time span: 6 days
  • Total changes: +1123 -0 (net: +1123)
  • Average files per commit: 7.5

👥 Authors:
  • copilot-swe-agent[bot]: 1 commits, +0 -0, 0 unique files
  • GitHub Actions: 1 commits, +1123 -0, 15 unique files

📝 Recent Commits:
  • ba15795 (2025-07-18) copilot-swe-agent[bot]: Initial plan
  • d45bce2 (2025-07-11) GitHub Actions: chore: Update CHANGELOG.md
    └─ 15 files, +1123 -0

📁 Most Frequently Changed Files:
  • .devcontainer/Dockerfile: 1 times
  • .devcontainer/devcontainer.json: 1 times
  • .devcontainer/init-firewall.sh: 1 times
```

## run_devcontainer_claude_code.ps1

PowerShell script for setting up and connecting to a DevContainer environment using Docker or Podman on Windows.

### Usage

```powershell
.\Script\run_devcontainer_claude_code.ps1 -Backend docker
.\Script\run_devcontainer_claude_code.ps1 -Backend podman
```