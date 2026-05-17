# core/commit.py — create and read commit objects
import time, os
from typing import Optional
from core import objects, refs, tree, index
from core.repository import Repository


def create_commit(repo: Repository, message: str, author: str = 'You') -> str:
    """
    Full commit flow:
      1. Build tree from index
      2. Get parent SHA from HEAD (None if first commit)
      3. Serialize commit object
      4. Write to object store
      5. Advance HEAD (or the branch HEAD points to)

    Commit format (plain text, same as Git):
      tree <sha>
      parent <sha>        (optional — omitted for root commit)
      author <name> <timestamp>
      committer <name> <timestamp>

      <blank line>
      <message>
    """
    staged = index.read_index(repo)
    if not staged:
        raise Exception("Nothing to commit. Stage files with 'pls add'.")

    tree_sha = tree.write_tree(repo)
    parent   = refs.resolve_head(repo)          # None on first commit
    ts       = int(time.time())

    lines = [
        f"tree {tree_sha}",
        f"author {author} <{author.lower()}@local> {ts}",
        f"committer {author} <{author.lower()}@local> {ts}",
    ]
    if parent:
        lines.insert(1, f"parent {parent}")  # parent comes after tree

    lines.append('')                          # blank line separates headers from body
    lines.append(message)

    commit_data = '\n'.join(lines).encode()
    commit_sha  = objects.hash_object(commit_data, 'commit', repo.path)

    refs.update_head(repo, commit_sha)         # advance branch pointer
    return commit_sha


def read_commit(repo: Repository, sha: str) -> dict:
    """
    Parse a commit object. Returns a dict with keys:
      tree, parent (optional), author, committer, message
    """
    _, raw = objects.read_object(sha, repo.path)
    text   = raw.decode()

    # Split headers from message body at the blank line
    parts   = text.split('\n\n', 1)
    headers = parts[0]
    message = parts[1] if len(parts) > 1 else ''

    result = {'message': message.strip()}
    for line in headers.splitlines():
        key, _, value = line.partition(' ')   # 'tree sha', 'parent sha', etc.
        result[key] = value

    return result


def log(repo: Repository) -> None:
    """Walk parent chain from HEAD and print each commit."""
    sha = refs.resolve_head(repo)
    if not sha:
        print("No commits yet.")
        return

    while sha:
        c = read_commit(repo, sha)
        print(f"\033[33mcommit {sha}\033[0m")    # yellow SHA
        print(f"Author: {c.get('author', 'unknown')}")
        print(f"\n    {c['message']}\n")
        sha = c.get('parent')                  # None stops the loop


def find_merge_base(repo: Repository, sha_a: str, sha_b: str) -> Optional[str]:
    """
    BFS from both tips. First commit reachable from both is the merge base.
    Used by `pls merge` to find the common ancestor.
    """
    def ancestors(start_sha: str) -> set[str]:
        seen, queue = set(), [start_sha]
        while queue:
            sha = queue.pop(0)
            if sha in seen: continue
            seen.add(sha)
            c = read_commit(repo, sha)
            if 'parent' in c: queue.append(c['parent'])
        return seen

    ancestors_a = ancestors(sha_a)
    for sha in ancestors(sha_b):
        if sha in ancestors_a:
            return sha    # first common ancestor found
    return None
