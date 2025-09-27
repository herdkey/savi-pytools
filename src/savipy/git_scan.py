#!/usr/bin/env python3

import os
import subprocess
import sys

# ANSI colors (no external deps)
RESET = '\033[0m'
BOLD = '\033[1m'
CYAN = '\033[36m'
YELLOW = '\033[33m'
MAGENTA = '\033[35m'
RED = '\033[31m'


def run_git(args: list[str], cwd: str) -> tuple[str, bool]:
    try:
        out = subprocess.check_output(
            ['git'] + args, cwd=cwd, stderr=subprocess.DEVNULL, text=True
        )
        return out.strip(), True
    except subprocess.CalledProcessError:
        return '', False
    except FileNotFoundError:
        print('git not found on PATH', file=sys.stderr)
        sys.exit(1)


def is_git_repo(path: str) -> bool:
    # Fast path: if .git exists (dir or file), treat as repo
    dotgit = os.path.join(path, '.git')
    if os.path.isdir(dotgit) or os.path.isfile(dotgit):
        return True
    # Fallback: ask git (handles bare/worktrees)
    out, ok = run_git(['rev-parse', '--is-inside-work-tree'], path)
    return ok and out == 'true'


def current_branch(path: str) -> tuple[str, bool, str | None]:
    """
    Returns:
      (branch_display, is_main, extra_note)
      - branch_display: 'main', 'feature/xyz', or 'DETACHED@<sha>'
      - is_main: True if exactly 'main'
      - extra_note: optional additional info (e.g., base ref)
    """
    name, ok = run_git(['rev-parse', '--abbrev-ref', 'HEAD'], path)
    if not ok:
        return 'UNKNOWN', False, None

    if name == 'HEAD':
        sha, _ = run_git(['rev-parse', '--short', 'HEAD'], path)
        return f'DETACHED@{sha or "?"}', False, None

    return name, name == 'main', None


def diff_shortstat(path: str) -> tuple[bool, str]:
    """
    Returns:
      (has_diff, summary)
      Uses 'git diff --shortstat HEAD' so staged + unstaged vs HEAD.
    """
    # If no diff, shortstat returns empty output
    summary, ok = run_git(['diff', '--shortstat', 'HEAD'], path)
    if not ok:
        return False, ''
    return bool(summary), summary


def print_summary(
    relpath: str, branch_disp: str, is_main: bool, has_diff: bool, diff_sum: str
) -> None:
    header = f'{BOLD}{CYAN}{relpath}{RESET}'
    lines = [header]

    if not is_main:
        color = MAGENTA if branch_disp.startswith('DETACHED@') else YELLOW
        lines.append(f'  branch: {color}{branch_disp}{RESET}')

    if has_diff:
        lines.append(f'  diff:   {RED}{diff_sum}{RESET}')

    print('\n'.join(lines))
    print()  # blank line between folders


def walk_repos(root: str) -> None:
    root = os.path.abspath(root)
    for dirpath, dirnames, _filenames in os.walk(root):
        # Never descend into .git directories
        if '.git' in dirnames:
            dirnames.remove('.git')

        if is_git_repo(dirpath):
            relpath = os.path.relpath(dirpath, root)
            if relpath == '.':
                relpath = os.path.basename(root.rstrip(os.sep)) or '.'

            branch_disp, is_main, _ = current_branch(dirpath)
            has_diff, diff_sum = diff_shortstat(dirpath)

            if (not is_main) or has_diff:
                print_summary(relpath, branch_disp, is_main, has_diff, diff_sum)

            # Do NOT recurse further inside a repo (avoids submodules)
            dirnames[:] = []
            continue

        # Otherwise, keep walking normally


def main() -> None:
    start_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    if not os.path.isdir(start_dir):
        print(f'Not a directory: {start_dir}', file=sys.stderr)
        sys.exit(2)
    walk_repos(start_dir)


if __name__ == '__main__':
    main()
