# commands/cmd_status.py
import os
from core import objects, index
from core.repository import Repository

def run(args):
    repo   = Repository.find()
    staged = index.read_index(repo)

    print("Changes to be committed:")
    for path in staged:
        print(f"  \033[32m  staged:   {path}\033[0m")

    print("\nChanges not staged for commit:")
    for path, staged_sha in staged.items():
        abs_path = repo.work_path(path)
        if not os.path.exists(abs_path):
            print(f"  \033[31m  deleted:  {path}\033[0m")
            continue
        # Re-hash without writing — just compute what the SHA would be
        with open(abs_path, 'rb') as f:
            current_data = f.read()
        current_sha = objects.hash_object(current_data, 'blob', repo.path,
                                            write=False)
        if current_sha != staged_sha:
            print(f"  \033[31m  modified: {path}\033[0m")

    print("\nUntracked files:")
    _find_untracked(repo, repo.path, staged)

def _find_untracked(repo, directory, staged):
    for entry in sorted(os.scandir(directory), key=lambda e: e.name):
        if entry.name == '.vcs':
            continue
        rel = os.path.relpath(entry.path, repo.path)
        if entry.is_file() and rel not in staged:
            print(f"  \033[90m  {rel}\033[0m")
        elif entry.is_dir():
            _find_untracked(repo, entry.path, staged)
