# commands/cmd_branch.py
import os
from core import refs
from core.repository import Repository

def run(args):
    repo = Repository.find()

    if args.delete:
        _delete_branch(repo, args.delete)
    elif args.name:
        # Create new branch at current HEAD
        sha = refs.resolve_head(repo)
        if not sha:
            print("error: no commits yet — cannot create a branch")
            return
        refs.create_branch(repo, args.name, sha)
        print(f"Created branch '{args.name}'")
    else:
        # List all branches, mark current with *
        current_head = refs.read_head(repo)
        for branch in refs.list_branches(repo):
            is_current = f'refs/heads/{branch}' in current_head
            marker     = '\033[32m* ' if is_current else '  '
            reset      = '\033[0m' if is_current else ''
            print(f"{marker}{branch}{reset}")

def _delete_branch(repo, name):
    path = repo.vcs_path('refs', 'heads', name)
    if not os.path.exists(path):
        print(f"error: branch '{name}' not found")
        return
    # Prevent deleting the currently checked-out branch
    current_head = refs.read_head(repo)
    if f'refs/heads/{name}' in current_head:
        print(f"error: cannot delete '{name}' — currently checked out")
        return
    os.remove(path)
    print(f"Deleted branch '{name}'")
