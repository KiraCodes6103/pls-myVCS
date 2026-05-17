# commands/cmd_add.py
import os
from core import objects, index
from core.repository import Repository

def run(args):
    repo = Repository.find()

    for filepath in args.files:
        abs_path = os.path.abspath(filepath)
        rel_path = os.path.relpath(abs_path, repo.path)

        # Guard: file must exist
        if not os.path.exists(abs_path):
            print(f"error: '{filepath}' does not exist")
            continue

        # Guard: file must be inside the repo
        if rel_path.startswith('..'):
            print(f"error: '{filepath}' is outside the repository")
            continue

        # Guard: never stage .vcs/ internals
        if rel_path.startswith('.vcs'):
            print(f"error: cannot stage .vcs/ directory")
            continue

        with open(abs_path, 'rb') as f:
            data = f.read()

        sha = objects.hash_object(data, 'blob', repo.path)
        index.add_entry(repo, rel_path, sha)
        print(f"staged: {rel_path}")
