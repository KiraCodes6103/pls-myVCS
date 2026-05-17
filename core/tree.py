import os
from dataclasses import dataclass
from core import objects, index
from core.repository import Repository


@dataclass
class TreeEntry:
    mode: str    # '100644' = regular file, '040000' = directory
    name: str    # filename or dirname (NOT full path)
    sha:  str    # blob sha for files, tree sha for dirs


def write_tree(repo: Repository) -> str:
    entries = index.read_index(repo)
    return _build_tree(repo, entries, prefix='')


def _build_tree(repo: Repository, entries: dict, prefix: str) -> str:
    tree_entries = []
    subdirs      = set()

    for path, sha in entries.items():
        if not path.startswith(prefix):
            continue

        rest = path[len(prefix):]         # strip the prefix

        if '/' in rest:
            # File is in a subdirectory — collect the subdir name
            subdir = rest.split('/')[0]
            subdirs.add(subdir)
        else:
            # Direct file in this directory
            tree_entries.append(TreeEntry('100644', rest, sha))

    # Recursively build subtrees for each subdirectory
    for subdir in sorted(subdirs):
        sub_sha = _build_tree(repo, entries, prefix + subdir + '/')
        tree_entries.append(TreeEntry('040000', subdir, sub_sha))

    # Serialize: each entry is "<mode> <name>\0<sha_bytes>"
    buf = b''
    for entry in sorted(tree_entries, key=lambda e: e.name):
        buf += f"{entry.mode} {entry.name}\0".encode()
        buf += bytes.fromhex(entry.sha)   # store SHA as raw 32 bytes (not hex)

    return objects.hash_object(buf, 'tree', repo.path)


def read_tree(repo: Repository, tree_sha: str) -> list[TreeEntry]:
    """Parse a tree object back into a list of TreeEntry."""
    _, raw = objects.read_object(tree_sha, repo.path)
    entries = []
    i = 0
    while i < len(raw):
        null_pos = raw.index(b'\0', i)
        header   = raw[i:null_pos].decode()         # "100644 filename"
        mode, name = header.split(' ', 1)
        sha = raw[null_pos+1 : null_pos+33].hex()  # 32 raw bytes → hex
        entries.append(TreeEntry(mode, name, sha))
        i = null_pos + 33
    return entries


def restore_tree(repo: Repository, tree_sha: str, dest: str) -> None:
    """
    Restore all files from a tree object into dest directory.
    Used by checkout — recursively writes every file from the tree.
    """
    os.makedirs(dest, exist_ok=True)
    for entry in read_tree(repo, tree_sha):
        full_path = os.path.join(dest, entry.name)
        if entry.mode == '100644':         # file
            _, content = objects.read_object(entry.sha, repo.path)
            with open(full_path, 'wb') as f:
                f.write(content)
        else:                               # subtree (directory)
            restore_tree(repo, entry.sha, full_path)
