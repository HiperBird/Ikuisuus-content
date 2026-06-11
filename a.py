#!/usr/bin/env python3
"""
List all deletions and renames from a commit up to the current HEAD.
Usage: python inspect_commit.py [commit_hash]
"""

import subprocess
import sys
from pathlib import Path

def run_git(args, cwd):
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def main():
    base_commit = sys.argv[1] if len(sys.argv) > 1 else "c1243dfdc67dec1fcff479c4572167e5e14d603c"
    cwd = Path.cwd()

    # Get the current HEAD commit (to show the range)
    head_stdout, _, _ = run_git(["git", "rev-parse", "HEAD"], cwd)
    current_head = head_stdout[:12] if head_stdout else "HEAD"

    # Show diff from base_commit to HEAD, only deletions and renames
    # --diff-filter=DR : D(eleted), R(ename)
    # --find-renames : detect renames
    # --name-status : show status and filenames
    cmd = ["git", "diff", "--diff-filter=DR", "--find-renames", "--name-status", f"{base_commit}..HEAD"]
    stdout, stderr, code = run_git(cmd, cwd)
    if code != 0:
        print(f"Error: {stderr}")
        sys.exit(1)

    deletions = []
    renames = []
    for line in stdout.split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        status = parts[0]
        if status == 'D':
            deletions.append(parts[1])
        elif status.startswith('R'):
            # Format: R<similarity>   old   new
            if len(parts) >= 3:
                renames.append((parts[1], parts[2]))
            else:
                renames.append((parts[1], parts[1]))

    print(f"From commit: {base_commit[:12]}")
    print(f"To HEAD:     {current_head}")
    print("\n=== DELETIONS ===")
    for f in deletions:
        print(f"  {f}")
    if not deletions:
        print("  None")
    print("\n=== RENAMES ===")
    for old, new in renames:
        print(f"  {old} -> {new}")
    if not renames:
        print("  None")
    print(f"\nTotal deletions: {len(deletions)}")
    print(f"Total renames:   {len(renames)}")

if __name__ == "__main__":
    main()