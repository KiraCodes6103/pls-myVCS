# commands/cmd_diff.py
import os
from core import objects, refs, commit, index
from core.repository import Repository
from diff.myers import diff, format_diff

def run(args):
    repo = Repository.find()
    if args.commit_a and args.commit_b:
        _diff_commits(repo, args.commit_a, args.commit_b)
    elif args.cached:
        _diff_cached(repo)
    else:
        _diff_working(repo)

def _diff_working(repo):
    """Working directory vs index (what would change if you ran add)."""
    staged = index.read_index(repo)
    for path, staged_sha in staged.items():
        abs_path = repo.work_path(path)
        if not os.path.exists(abs_path):
            continue
        with open(abs_path, 'r', errors='replace') as f:
            current_lines = f.readlines()
        _, blob_data = objects.read_object(staged_sha, repo.path)
        staged_lines = blob_data.decode(errors='replace').splitlines(keepends=True)
        if current_lines != staged_lines:
            edits = diff(staged_lines, current_lines)
            print(format_diff(edits, f"a/{path}", f"b/{path}"))

def _diff_cached(repo):
    """Index vs last commit (what would be recorded if you committed now)."""
    sha = refs.resolve_head(repo)
    if not sha:
        print("No commits yet.")
        return
    committed = _flat_tree(repo, commit.read_commit(repo, sha)['tree'])
    staged    = index.read_index(repo)
    for path in sorted(set(committed) | set(staged)):
        _print_file_diff(repo, path, committed.get(path), staged.get(path))

def _diff_commits(repo, sha_a, sha_b):
    """Two arbitrary commits."""
    tree_a = _flat_tree(repo, commit.read_commit(repo, sha_a)['tree'])
    tree_b = _flat_tree(repo, commit.read_commit(repo, sha_b)['tree'])
    for path in sorted(set(tree_a) | set(tree_b)):
        _print_file_diff(repo, path, tree_a.get(path), tree_b.get(path))

def _print_file_diff(repo, path, sha_a, sha_b):
    def lines(sha):
        if sha is None: return []
        _, data = objects.read_object(sha, repo.path)
        return data.decode(errors='replace').splitlines(keepends=True)
    a, b = lines(sha_a), lines(sha_b)
    if a != b:
        print(format_diff(diff(a, b), f"a/{path}", f"b/{path}"))

def _flat_tree(repo, tree_sha, prefix=''):
    """Recursively flatten a tree into {rel_path: blob_sha}."""
    from core.tree import read_tree
    result = {}
    for entry in read_tree(repo, tree_sha):
        path = f"{prefix}/{entry.name}" if prefix else entry.name
        if entry.mode == '100644':
            result[path] = entry.sha
        else:
            result.update(_flat_tree(repo, entry.sha, path))
    return result
