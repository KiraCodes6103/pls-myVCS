#!/usr/bin/env python3
# This file contains ONLY argparse wiring. All logic lives in commands/.
import argparse, sys
from commands import (
    cmd_init, cmd_hash_object, cmd_cat_file,
    cmd_add, cmd_status, cmd_commit, cmd_log,
    cmd_branch, cmd_checkout, cmd_diff, cmd_merge
)


def main():
    p   = argparse.ArgumentParser(prog='pls', description='PLS')
    sub = p.add_subparsers(dest='command', required=True)

    # ── Foundation commands ───────────────────────────────────────────
    sub.add_parser('init').set_defaults(func=cmd_init.run)

    s = sub.add_parser('hash-object')
    s.add_argument('file')
    s.add_argument('-w', '--write', action='store_true')
    s.set_defaults(func=cmd_hash_object.run)

    s = sub.add_parser('cat-file')
    s.add_argument('sha')
    s.add_argument('-t', dest='type_only', action='store_true')
    s.add_argument('-s', dest='size_only', action='store_true')
    s.set_defaults(func=cmd_cat_file.run)

    # ── Staging commands ──────────────────────────────────────────────
    s = sub.add_parser('add')
    s.add_argument('files', nargs='+')
    s.set_defaults(func=cmd_add.run)

    sub.add_parser('status').set_defaults(func=cmd_status.run)

    # ── History commands ──────────────────────────────────────────────
    s = sub.add_parser('commit')
    s.add_argument('-m', '--message', required=True)
    s.set_defaults(func=cmd_commit.run)

    s = sub.add_parser('log')
    s.add_argument('-n', dest='max_count', type=int, default=None)
    s.set_defaults(func=cmd_log.run)

    # ── Branch commands ───────────────────────────────────────────────
    s = sub.add_parser('branch')
    s.add_argument('name', nargs='?')
    s.add_argument('-d', '--delete', metavar='BRANCH')
    s.set_defaults(func=cmd_branch.run)

    s = sub.add_parser('checkout')
    s.add_argument('target')
    s.set_defaults(func=cmd_checkout.run)

    # ── Diff commands ─────────────────────────────────────────────────
    s = sub.add_parser('diff')
    s.add_argument('commit_a', nargs='?')
    s.add_argument('commit_b', nargs='?')
    s.add_argument('--cached', action='store_true')
    s.set_defaults(func=cmd_diff.run)

    s = sub.add_parser('merge')
    s.add_argument('branch')
    s.set_defaults(func=cmd_merge.run)

    # ── Run ───────────────────────────────────────────────────────────
    args = p.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"\033[31merror:\033[0m {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
