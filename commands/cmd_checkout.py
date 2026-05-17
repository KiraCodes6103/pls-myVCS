# commands/cmd_checkout.py
from core import refs, commit, tree, index
from core.repository import Repository

def run(args):
    repo = Repository.find()

    # Resolve target — branch name or raw commit SHA
    try:
        target_sha = refs.get_branch_sha(repo, args.target)
        is_branch  = True
    except FileNotFoundError:
        target_sha = args.target     # treat as raw SHA (detached HEAD)
        is_branch  = False

    try:
        c = commit.read_commit(repo, target_sha)
    except FileNotFoundError:
        print(f"error: '{args.target}' is not a branch or commit SHA")
        return

    # 1. Restore working directory files from the commit's tree
    tree.restore_tree(repo, c['tree'], repo.path)

    # 2. CRITICAL: update the index to match the restored tree
    new_entries = {}
    _collect_tree_entries(repo, c['tree'], '', new_entries)
    index.write_index(repo, new_entries)

    # 3. Update HEAD
    if is_branch:
        refs.set_head_to_branch(repo, args.target)
        print(f"Switched to branch '{args.target}'")
    else:
        with open(repo.vcs_path('HEAD'), 'w') as f:
            f.write(target_sha + '\n')
        print(f"HEAD is now at {target_sha[:7]} (detached)")

def _collect_tree_entries(repo, tree_sha, prefix, result):
    """Flatten a tree recursively into {rel_path: blob_sha}."""
    from core.tree import read_tree
    for entry in read_tree(repo, tree_sha):
        path = f"{prefix}/{entry.name}" if prefix else entry.name
        if entry.mode == '100644':
            result[path] = entry.sha
        else:
            _collect_tree_entries(repo, entry.sha, path, result)
