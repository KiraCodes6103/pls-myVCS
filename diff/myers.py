# diff/myers.py — Myers O(ND) diff algorithm
# Returns a list of Edit objects describing how to turn `a` into `b`.
from dataclasses import dataclass
from enum import Enum


class Op(Enum):
    KEEP   = 'keep'    # line matches — show with no prefix
    INSERT = 'insert'  # line added   — show with '+'
    DELETE = 'delete'  # line removed — show with '-'


@dataclass
class Edit:
    op:   Op
    line: str           # the actual line content


def diff(a: list[str], b: list[str]) -> list[Edit]:
    """
    Compute the shortest edit script from a to b using Myers algorithm.

    Core idea: search outward from D=0 (no edits) to D=1 (one edit) etc.
    For each D, we explore all possible 'k-diagonals' (k = x - y).
    We track the furthest-reaching x on each diagonal in array V.
    When we reach (len_a, len_b), we backtrack V snapshots to get the path.
    """
    n, m = len(a), len(b)
    max_d = n + m                    # worst case: delete all of a, insert all of b

    # v[k] = furthest x reached on diagonal k (k = x - y)
    # We use offset of max_d so negative k values become valid indices
    v    = [0] * (2 * max_d + 1)
    v[1 + max_d] = 0                 # start at x=0 on diagonal k=1 (convention)
    trace = []                        # save V snapshots to backtrack later

    for d in range(max_d + 1):
        trace.append(v[:])            # snapshot before this round

        for k in range(-d, d + 1, 2):   # only even or odd k's matter at each D
            ki = k + max_d             # shifted index

            # Choose: go right (delete from a) or go down (insert from b)?
            if k == -d or (k != d and v[ki - 1] < v[ki + 1]):
                x = v[ki + 1]         # came from diagonal k+1 → move down (insert)
            else:
                x = v[ki - 1] + 1     # came from diagonal k-1 → move right (delete)

            y = x - k                  # y is always x - k by definition

            # Slide diagonally as far as possible (free matching moves)
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[ki] = x

            if x >= n and y >= m:     # reached the end!
                return _backtrack(trace, a, b, n, m, max_d, d)

    return []                         # empty if a == b


def _backtrack(trace, a, b, n, m, max_d, d) -> list[Edit]:
    """
    Reconstruct the edit path by walking backwards through V snapshots.
    Start at (n, m) and work back to (0, 0).
    """
    edits = []
    x, y = n, m

    for curr_d in range(d, 0, -1):
        v  = trace[curr_d]
        k  = x - y
        ki = k + max_d

        # Determine how we arrived at current k
        if k == -curr_d or (k != curr_d and v[ki - 1] < v[ki + 1]):
            prev_k = k + 1            # came from k+1 (insertion)
        else:
            prev_k = k - 1            # came from k-1 (deletion)

        prev_x = v[prev_k + max_d]
        prev_y = prev_x - prev_k

        # Walk the diagonal snake (matching lines) backwards
        while x > prev_x and y > prev_y:
            edits.append(Edit(Op.KEEP, a[x - 1]))
            x -= 1; y -= 1

        # Record the actual edit (deletion or insertion)
        if x > prev_x:
            edits.append(Edit(Op.DELETE, a[x - 1]))
            x -= 1
        elif y > prev_y:
            edits.append(Edit(Op.INSERT, b[y - 1]))
            y -= 1

    edits.reverse()                   # we built it backwards
    return edits


def format_diff(edits: list[Edit], file_a='a', file_b='b') -> str:
    """Render edits as a unified diff string."""
    lines = [f"--- {file_a}", f"+++ {file_b}"]
    for edit in edits:
        if   edit.op == Op.KEEP:   lines.append(f"  {edit.line}")
        elif edit.op == Op.INSERT: lines.append(f"+ {edit.line}")
        elif edit.op == Op.DELETE: lines.append(f"- {edit.line}")
    return '\n'.join(lines)
