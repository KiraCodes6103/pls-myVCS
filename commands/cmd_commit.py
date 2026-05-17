# commands/cmd_commit.py
from core import commit, index, refs
from core.repository import Repository

def run(args):
    repo = Repository.find()

    if not index.read_index(repo):
        print("nothing to commit (use 'pls add' to stage files)")
        return

    sha    = commit.create_commit(repo, message=args.message)
    branch = _current_branch(repo)
    staged = index.read_index(repo)
    print(f"[{branch} {sha[:7]}] {args.message}")
    print(f"  {len(staged)} file(s) committed")

def _current_branch(repo):
    head = refs.read_head(repo)
    if head.startswith('ref: refs/heads/'):
        return head[len('ref: refs/heads/'):]
    return head[:7]    # detached HEAD — show short SHA
