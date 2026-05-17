# core/refs.py — HEAD and branch references (all just files)
import os
from typing import Optional
from core.repository import Repository


def read_head(repo: Repository) -> str:
    """Return the raw content of HEAD (may be a symbolic ref or a sha)."""
    with open(repo.vcs_path('HEAD')) as f:
        return f.read().strip()


def resolve_head(repo: Repository) -> Optional[str]:
    """
    Resolve HEAD all the way to a commit SHA.
    Returns None if the branch exists but has no commits yet.

    HEAD contains either:
      "ref: refs/heads/main"   → symbolic ref, follow the chain
      "a3f9d2..."              → detached HEAD, return directly
    """
    head = read_head(repo)

    if head.startswith('ref: '):
        ref_path = head[5:]                       # strip 'ref: '
        full_path = repo.vcs_path(*ref_path.split('/'))
        if not os.path.exists(full_path):
            return None                            # branch file doesn't exist yet
        with open(full_path) as f:
            content = f.read().strip()
        return content if content else None

    return head if head else None                 # already a SHA


def update_head(repo: Repository, new_sha: str) -> None:
    """
    After a commit: if HEAD is a symbolic ref, update the branch file.
    If HEAD is detached, update HEAD directly.
    """
    head = read_head(repo)

    if head.startswith('ref: '):
        ref_path  = head[5:]
        full_path = repo.vcs_path(*ref_path.split('/'))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(new_sha + '\n')
    else:
        # Detached HEAD — update HEAD directly
        with open(repo.vcs_path('HEAD'), 'w') as f:
            f.write(new_sha + '\n')


def create_branch(repo: Repository, name: str, sha: str) -> None:
    """Create a new branch pointing at sha."""
    path = repo.vcs_path('refs', 'heads', name)
    if os.path.exists(path):
        raise Exception(f"Branch '{name}' already exists")
    with open(path, 'w') as f:
        f.write(sha + '\n')


def get_branch_sha(repo: Repository, name: str) -> str:
    """Return the commit SHA a branch points to."""
    path = repo.vcs_path('refs', 'heads', name)
    with open(path) as f:
        return f.read().strip()


def set_head_to_branch(repo: Repository, name: str) -> None:
    """Make HEAD point to a branch (used by checkout)."""
    with open(repo.vcs_path('HEAD'), 'w') as f:
        f.write(f'ref: refs/heads/{name}\n')


def list_branches(repo: Repository) -> list[str]:
    """Return all branch names."""
    heads_dir = repo.vcs_path('refs', 'heads')
    return sorted(os.listdir(heads_dir))
