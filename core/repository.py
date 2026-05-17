# repository.py — find and create the .vcs directory
import os


class Repository:
    """Represents a pls repository rooted at self.path."""

    def __init__(self, path: str):
        self.path    = path                         # working directory root
        self.vcs_dir = os.path.join(path, '.vcs')   # all metadata lives here

    # Helper Functions

    def vcs_path(self, *parts) -> str:
        """Build a path inside .vcs/. e.g. repo.vcs_path('refs','heads','main')"""
        return os.path.join(self.vcs_dir, *parts)

    def work_path(self, *parts) -> str:
        """Build a path inside the working directory."""
        return os.path.join(self.path, *parts)

    # Factory Methods

    @classmethod
    def init(cls, path: str) -> 'Repository':
        """Create a new repository. Idempotent — safe to run twice."""
        repo = cls(path)
        dirs = [
            repo.vcs_path('objects'),
            repo.vcs_path('refs', 'heads'),
            repo.vcs_path('refs', 'tags'),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

        # HEAD starts pointing at main (branch doesn't exist yet — that's ok)
        head_path = repo.vcs_path('HEAD')
        if not os.path.exists(head_path):
            with open(head_path, 'w') as f:
                f.write('ref: refs/heads/main\n')

        print(f"Initialized empty PLS repository in {repo.vcs_dir}")
        return repo

    @classmethod
    def find(cls, start: str = '.') -> 'Repository':
        """
        Walk up from start until we find a .vcs/ directory.
        Raises an error if none found (not inside a repo).
        """
        path = os.path.abspath(start)

        while True:
            candidate = os.path.join(path, '.vcs')
            if os.path.isdir(candidate):
                return cls(path)           # found it!

            parent = os.path.dirname(path)
            if parent == path:             # hit filesystem root
                raise Exception("Not a pls repository (no .vcs/ found)")
            path = parent
