#!/usr/bin/env python3
"""
Claude Code Tool: Commit Analysis
=================================
This tool analyzes recent commits in a Git repository and provides insights
about commit patterns, authors, changes, and activity.

Usage:
    python3 analyze_commits.py [--count N] [--output FORMAT]

Arguments:
    --count N       Number of recent commits to analyze (default: 10)
    --output FORMAT Output format: 'text' or 'json' (default: 'text')

Examples:
    python3 analyze_commits.py
    python3 analyze_commits.py --count 20 --output json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any
import re


class CommitAnalyzer:
    """Analyzes Git commits and provides insights."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def run_git_command(self, args: List[str]) -> str:
        """Run a git command and return the output."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}", file=sys.stderr)
            return ""
    
    def get_recent_commits(self, count: int) -> List[Dict[str, Any]]:
        """Get recent commits with detailed information."""
        commits = []
        
        # Get commit hashes and basic info
        log_output = self.run_git_command([
            "log", "--oneline", f"-{count}", "--pretty=format:%H|%an|%ae|%ad|%s",
            "--date=iso"
        ])
        
        if not log_output:
            return commits
        
        for line in log_output.split('\n'):
            if not line.strip():
                continue
                
            parts = line.split('|', 4)
            if len(parts) < 5:
                continue
                
            commit_hash, author_name, author_email, date_str, message = parts
            
            # Get file changes for this commit
            stat_output = self.run_git_command([
                "show", "--stat", "--format=", commit_hash
            ])
            
            # Parse file changes
            files_changed = []
            insertions = 0
            deletions = 0
            
            for stat_line in stat_output.split('\n'):
                if '|' in stat_line and ('+' in stat_line or '-' in stat_line):
                    # Extract filename
                    filename = stat_line.split('|')[0].strip()
                    files_changed.append(filename)
                elif 'insertion' in stat_line or 'deletion' in stat_line:
                    # Parse summary line like "15 files changed, 1123 insertions(+)"
                    numbers = re.findall(r'\d+', stat_line)
                    if len(numbers) >= 2:
                        insertions = int(numbers[1]) if 'insertion' in stat_line else 0
                        if len(numbers) >= 3:
                            deletions = int(numbers[2]) if 'deletion' in stat_line else 0
                    elif len(numbers) == 1 and 'insertion' in stat_line:
                        insertions = int(numbers[0])
                    elif len(numbers) == 1 and 'deletion' in stat_line:
                        deletions = int(numbers[0])
            
            commit_info = {
                "hash": commit_hash,
                "short_hash": commit_hash[:7],
                "author_name": author_name,
                "author_email": author_email,
                "date": date_str,
                "message": message,
                "files_changed": files_changed,
                "files_count": len(files_changed),
                "insertions": insertions,
                "deletions": deletions,
                "net_changes": insertions - deletions
            }
            
            commits.append(commit_info)
        
        return commits
    
    def analyze_patterns(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in the commits."""
        if not commits:
            return {}
        
        # Author analysis
        authors = {}
        for commit in commits:
            author = commit["author_name"]
            if author not in authors:
                authors[author] = {
                    "commit_count": 0,
                    "total_insertions": 0,
                    "total_deletions": 0,
                    "files_touched": set()
                }
            
            authors[author]["commit_count"] += 1
            authors[author]["total_insertions"] += commit["insertions"]
            authors[author]["total_deletions"] += commit["deletions"]
            authors[author]["files_touched"].update(commit["files_changed"])
        
        # Convert sets to counts for JSON serialization
        for author_data in authors.values():
            author_data["unique_files_touched"] = len(author_data["files_touched"])
            del author_data["files_touched"]
        
        # File analysis
        file_frequency = {}
        for commit in commits:
            for file in commit["files_changed"]:
                file_frequency[file] = file_frequency.get(file, 0) + 1
        
        # Time analysis
        if commits:
            latest_commit = datetime.fromisoformat(commits[0]["date"].replace(' ', 'T'))
            oldest_commit = datetime.fromisoformat(commits[-1]["date"].replace(' ', 'T'))
            time_span = latest_commit - oldest_commit
        else:
            time_span = None
        
        # Commit size analysis
        total_insertions = sum(c["insertions"] for c in commits)
        total_deletions = sum(c["deletions"] for c in commits)
        avg_files_per_commit = sum(c["files_count"] for c in commits) / len(commits) if commits else 0
        
        return {
            "total_commits": len(commits),
            "authors": authors,
            "most_frequently_changed_files": dict(sorted(file_frequency.items(), 
                                                        key=lambda x: x[1], reverse=True)[:10]),
            "time_span_days": time_span.days if time_span else 0,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "net_changes": total_insertions - total_deletions,
            "average_files_per_commit": round(avg_files_per_commit, 1)
        }
    
    def format_text_output(self, commits: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Format analysis results as human-readable text."""
        output = []
        output.append("📊 Git Commit Analysis Report")
        output.append("=" * 40)
        output.append("")
        
        # Summary
        output.append(f"📈 Summary:")
        output.append(f"  • Total commits analyzed: {analysis['total_commits']}")
        output.append(f"  • Time span: {analysis['time_span_days']} days")
        output.append(f"  • Total changes: +{analysis['total_insertions']} -{analysis['total_deletions']} (net: {analysis['net_changes']:+})")
        output.append(f"  • Average files per commit: {analysis['average_files_per_commit']}")
        output.append("")
        
        # Authors
        output.append("👥 Authors:")
        for author, data in analysis["authors"].items():
            output.append(f"  • {author}: {data['commit_count']} commits, "
                         f"+{data['total_insertions']} -{data['total_deletions']}, "
                         f"{data['unique_files_touched']} unique files")
        output.append("")
        
        # Recent commits
        output.append("📝 Recent Commits:")
        for commit in commits[:5]:  # Show top 5
            date = commit["date"].split()[0]  # Just the date part
            output.append(f"  • {commit['short_hash']} ({date}) {commit['author_name']}: {commit['message']}")
            if commit["files_count"] > 0:
                output.append(f"    └─ {commit['files_count']} files, +{commit['insertions']} -{commit['deletions']}")
        
        if len(commits) > 5:
            output.append(f"  ... and {len(commits) - 5} more commits")
        output.append("")
        
        # Most changed files
        if analysis["most_frequently_changed_files"]:
            output.append("📁 Most Frequently Changed Files:")
            for file, count in list(analysis["most_frequently_changed_files"].items())[:5]:
                output.append(f"  • {file}: {count} times")
            output.append("")
        
        return "\n".join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze recent Git commits and provide insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('\n\n')[1]  # Use the usage examples from docstring
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=10,
        help="Number of recent commits to analyze (default: 10)"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format: 'text' or 'json' (default: 'text')"
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = CommitAnalyzer()
    
    # Get commits and analyze
    commits = analyzer.get_recent_commits(args.count)
    
    if not commits:
        print("No commits found or not in a Git repository.", file=sys.stderr)
        sys.exit(1)
    
    analysis = analyzer.analyze_patterns(commits)
    
    # Output results
    if args.output == "json":
        result = {
            "commits": commits,
            "analysis": analysis
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(analyzer.format_text_output(commits, analysis))


if __name__ == "__main__":
    main()