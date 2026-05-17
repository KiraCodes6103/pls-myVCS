# PLS

PLS is a small Git-like version control system written in Python. It is built as a learning project to understand how Git stores objects, tracks staged files, creates commits, moves branch references, restores snapshots, and computes diffs.

It is not a replacement for Git. It is a readable, hackable implementation of the core ideas behind a content-addressed VCS.

## Features

- Initialize a repository with a `.vcs/` metadata directory
- Store compressed content-addressed objects
- Hash and inspect blob objects
- Stage files through an index
- Create commits from staged snapshots
- Read commit history with `log`
- Create, list, delete, and checkout branches
- Checkout commits in detached HEAD mode
- Show working tree, staged, and commit-to-commit diffs
- Run a basic Myers diff implementation
- Attempt simple three-way merges with conflict markers

## Requirements

- Python 3.9+
- No runtime third-party dependencies
- `pytest` for running tests

## Quick Start

Clone the project:

```bash
git clone https://github.com/KiraCodes6103/pls-myVCS/
cd pls
```

Run the CLI:

```bash
./pls --help
```

Initialize a PLS repository:

```bash
./pls init
```

Create and commit a file:

```bash
echo "hello pls" > hello.txt
./pls add hello.txt
./pls status
./pls commit -m "initial commit"
```

View history:

```bash
./pls log
```

## Commands

### `pls init`

Creates a `.vcs/` directory in the current folder:

```bash
./pls init
```

The repository data is stored under:

```text
.vcs/
  HEAD
  index
  objects/
  refs/
    heads/
    tags/
```

### `pls hash-object`

Computes the SHA-256 object ID for a file.

```bash
./pls hash-object path/to/file
```

Write the object into `.vcs/objects`:

```bash
./pls hash-object -w path/to/file
```

### `pls cat-file`

Reads an object from the object store.

Print object contents:

```bash
./pls cat-file <sha>
```

Print object type:

```bash
./pls cat-file -t <sha>
```

Print object size:

```bash
./pls cat-file -s <sha>
```

### `pls add`

Stages one or more files:

```bash
./pls add file1.txt file2.txt
```

Staged files are recorded in `.vcs/index` as path-to-object mappings.

### `pls status`

Shows staged files, modified staged files, deleted staged files, and untracked files:

```bash
./pls status
```

### `pls commit`

Creates a commit from the current index:

```bash
./pls commit -m "describe the change"
```

Each commit stores:

- A root tree object
- An optional parent commit
- Author and committer metadata
- A commit message

### `pls log`

Prints commit history by walking parents from `HEAD`:

```bash
./pls log
```

### `pls branch`

List branches:

```bash
./pls branch
```

Create a branch at the current commit:

```bash
./pls branch feature-name
```

Delete a branch:

```bash
./pls branch -d feature-name
```

### `pls checkout`

Switch to a branch:

```bash
./pls checkout main
```

Checkout a raw commit SHA:

```bash
./pls checkout <commit-sha>
```

When checking out a commit, PLS restores files from the commit tree and updates the index to match that snapshot.

### `pls diff`

Show working directory changes compared with the index:

```bash
./pls diff
```

Show staged changes compared with the last commit:

```bash
./pls diff --cached
```

Show differences between two commits:

```bash
./pls diff <commit-a> <commit-b>
```

### `pls merge`

Attempts a basic three-way merge from another branch into the current branch:

```bash
./pls merge feature-name
```

If both sides edit the same lines, conflict markers are written into the merged content:

```text
<<<<<<< ours
...
=======
...
>>>>>>> theirs
```

After resolving conflicts, stage and commit the result:

```bash
./pls add conflicted-file.txt
./pls commit -m "resolve merge"
```

## How It Works

PLS follows the same broad model as Git:

1. File contents are stored as blob objects.
2. Directory snapshots are stored as tree objects.
3. Commits point to tree objects and parent commits.
4. Branches are files under `.vcs/refs/heads/`.
5. `HEAD` either points to a branch or stores a detached commit SHA.
6. The index tracks what will go into the next commit.

Objects are stored by SHA-256 hash:

```text
.vcs/objects/<first-2-sha-chars>/<remaining-sha-chars>
```

Before hashing, object content is prefixed with a Git-style header:

```text
<type> <size>\0<content>
```

Then the payload is compressed with `zlib` and written to disk.

## Project Structure

```text
pls
pls.py
commands/
  cmd_add.py
  cmd_branch.py
  cmd_cat_file.py
  cmd_checkout.py
  cmd_commit.py
  cmd_diff.py
  cmd_hash_object.py
  cmd_init.py
  cmd_log.py
  cmd_merge.py
  cmd_status.py
core/
  commit.py
  index.py
  objects.py
  refs.py
  repository.py
  tree.py
diff/
  myers.py
  merge.py
tests/
  test_objects.py
```

## Running Tests

Install pytest if needed:

```bash
python -m pip install pytest
```

Run tests:

```bash
python -m pytest
```

Or with your local virtual environment:

```bash
./plsenv/bin/python -m pytest
```

## Current Limitations

- PLS is educational and intentionally small.
- It does not implement the full Git object model or packfiles.
- It does not support remotes, clone, fetch, pull, or push.
- Checkout does not yet perform Git-style safety checks for overwriting local changes.
- Merge support is experimental and handles only simple cases.
- Automatic merge commit creation still needs more work.
- File mode support is minimal.

## Roadmap Ideas

- Add repository-safe checkout checks
- Improve merge commit creation and conflict workflows
- Add pathspec support
- Add better test coverage for branches, checkout, diff, and merge
- Add packaging so `pls` can be installed as a system command
- Add a cleaner index format

## License

No license has been added yet. Add one before publishing if you want others to use, modify, or distribute the project.
