# commands/cmd_merge.py
from core import refs, commit, index, objects
from core.repository import Repository
from diff.myers import diff, Op

def run(args):
    repo      = Repository.find()
    our_sha   = refs.resolve_head(repo)
    their_sha = refs.get_branch_sha(repo, args.branch)

    if our_sha == their_sha:
        print("Already up to date.")
        return

    base_sha  = commit.find_merge_base(repo, our_sha, their_sha)
    base_tree = _flat(repo, commit.read_commit(repo, base_sha)['tree']) if base_sha else {}
    our_tree  = _flat(repo, commit.read_commit(repo, our_sha)['tree'])
    their_tree= _flat(repo, commit.read_commit(repo, their_sha)['tree'])

    all_paths  = set(base_tree) | set(our_tree) | set(their_tree)
    new_index  = {}
    conflicts  = []

    for path in sorted(all_paths):
        result_sha, had_conflict = _merge_file(
            repo, path,
            base_tree.get(path), our_tree.get(path), their_tree.get(path)
        )
        if result_sha:
            new_index[path] = result_sha
        if had_conflict:
            conflicts.append(path)

    index.write_index(repo, new_index)

    if conflicts:
        print(f"CONFLICT in: {', '.join(conflicts)}")
        print("Fix conflicts then run 'pls commit' to finish.")
    else:
        sha = commit.create_merge_commit(
            repo, our_sha, their_sha, f"Merge branch '{args.branch}'"
        )
        print(f"Merged '{args.branch}' → [{sha[:7]}]")

def _merge_file(repo, path, base_sha, our_sha, their_sha):
    """Three-way merge for one file. Returns (result_sha, had_conflict)."""
    if our_sha == their_sha:   return our_sha, False   # identical
    if our_sha == base_sha:    return their_sha, False  # we didn't touch it
    if their_sha == base_sha:  return our_sha, False    # they didn't touch it

    # Both sides changed the same file — line-level merge needed
    def get_lines(sha):
        if sha is None: return []
        _, data = objects.read_object(sha, repo.path)
        return data.decode(errors='replace').splitlines(keepends=True)

    base_lines  = get_lines(base_sha)
    our_lines   = get_lines(our_sha)
    their_lines = get_lines(their_sha)

    merged, had_conflict = _three_way(base_lines, our_lines, their_lines)
    result_data = ''.join(merged).encode()
    result_sha  = objects.hash_object(result_data, 'blob', repo.path)
    return result_sha, had_conflict

def _three_way(base, ours, theirs):
    diff_ours   = diff(base, ours)
    diff_theirs = diff(base, theirs)
    our_changed   = {i for i, e in enumerate(diff_ours)   if e.op != Op.KEEP}
    their_changed = {i for i, e in enumerate(diff_theirs) if e.op != Op.KEEP}

    merged, had_conflict = [], False
    for i, base_line in enumerate(base):
        in_ours, in_theirs = i in our_changed, i in their_changed
        if not in_ours and not in_theirs:
            merged.append(base_line)
        elif in_ours and not in_theirs:
            merged.append(ours[i] if i < len(ours) else '')
        elif in_theirs and not in_ours:
            merged.append(theirs[i] if i < len(theirs) else '')
        else:
            had_conflict = True
            merged += ['<<<<<<< ours\n',
                        ours[i] if i < len(ours) else '',
                        '=======\n',
                        theirs[i] if i < len(theirs) else '',
                        '>>>>>>> theirs\n']
    return merged, had_conflict

def _flat(repo, tree_sha, prefix=''):
    from core.tree import read_tree
    result = {}
    for entry in read_tree(repo, tree_sha):
        path = f"{prefix}/{entry.name}" if prefix else entry.name
        if entry.mode == '100644': result[path] = entry.sha
        else: result.update(_flat(repo, entry.sha, path))
    return result
