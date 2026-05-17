import os
from core.repository import Repository


def read_index(repo: Repository) -> dict[str,str]:
    index_path = repo.vcs_path('index')
    if not os.path.exists(index_path):
        return {}
    
    entries = {}
    with open(index_path, 'r') as f:
        for line in f:
            line.strip()
            if not line:
                continue
            sha, path = line.split(' ',1)
            entries[path] = sha 

    return entries

def write_index(repo: Repository, entries: dict[str,str]) -> None:
    index_path = repo.vcs_path('index')
    with open(index_path,'w') as f:
        for entry in sorted(entries):
            path, sha = entry
            f.write(f"{sha} {path}\n")

def add_entry(repo: Repository, fileName: str, sha: str) -> None:
    entries = read_index(repo)
    entries[fileName] = sha
    write_index(repo, entries)

def remove_entry(repo: Repository, fileName: str) -> None:
    entries = read_index(repo)
    entries.pop(fileName,None)
    write_index(repo, entries)

def get_staged_files(repo: Repository) -> list:
    return list(read_index(repo).keys())
