# core/objects.py — hash, write, and read all VCS objects
import hashlib, zlib, os

# Object types we support
TYPES = {'blob', 'tree', 'commit'}


def hash_object(data: bytes, obj_type: str, repo_path: str, write=True) -> str:
    """
    Hash raw bytes into an object. Optionally write to disk.

    Git format:  <type> <size>\0<content>
    We prepend this header before hashing so two files with the same
    content but different types never collide.
    """
    assert obj_type in TYPES, f"Unknown type: {obj_type}"

    # 1. Build the full payload: header + raw data
    header = f"{obj_type} {len(data)}\0".encode("utf-8")
    full   = header + data

    # 2. SHA-256 hash the payload → this IS the object's identity
    sha = hashlib.sha256(full).hexdigest()   # 64-char hex string

    if write:
        # 3. Store at .vcs/objects/<first2>/<remaining62>
        obj_dir  = os.path.join(repo_path, '.vcs', 'objects', sha[:2])
        obj_path = os.path.join(obj_dir, sha[2:])
        os.makedirs(obj_dir, exist_ok=True)

        if not os.path.exists(obj_path):     # never overwrite — content is immutable
            with open(obj_path, 'wb') as f:
                f.write(zlib.compress(full))  # zlib compress to save space

    return sha


def read_object(sha: str, repo_path: str) -> tuple[str, bytes]:
    """
    Read an object by its SHA. Returns (type, raw_content).
    Raises FileNotFoundError if the object doesn't exist.
    """
    obj_path = os.path.join(repo_path, '.vcs', 'objects', sha[:2], sha[2:])

    with open(obj_path, 'rb') as f:
        full = zlib.decompress(f.read())

    # Split on the null byte to separate header from content
    header, content = full.split(b'\0', 1)
    obj_type, _ = header.decode().split(' ', 1)   # e.g. "blob 42"

    return obj_type, content


def object_exists(sha: str, repo_path: str) -> bool:
    obj_path = os.path.join(repo_path, '.vcs', 'objects', sha[:2], sha[2:])
    return os.path.exists(obj_path)
