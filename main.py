#!/usr/bin/env python3
"""Bulk find-and-replace across many text files.

Replaces *find* with *replace* in every matching file, with
optional regular expressions, case-insensitive matching, recursion
into subfolders, and a file-extension filter. Nothing is changed
with ``--dry-run``; with ``--backup`` each changed file gets a
``.bak`` copy first.
"""
import argparse
import glob
import os
import re
import shutil
import sys


def collect_files(patterns, recursive=False, extensions=None):
    """Expand file paths and globs into a sorted, deduplicated list."""
    found = []
    for pattern in patterns:
        if os.path.isfile(pattern):
            found.append(pattern)
            continue
        if os.path.isdir(pattern):
            if recursive:
                for root, _dirs, names in os.walk(pattern):
                    for name in names:
                        found.append(os.path.join(root, name))
            else:
                found.extend(os.path.join(pattern, name)
                             for name in os.listdir(pattern)
                             if os.path.isfile(os.path.join(pattern, name)))
            continue
        found.extend(glob.glob(pattern, recursive=recursive))
    files = sorted({os.path.abspath(p) for p in found
                    if os.path.isfile(p)})
    if extensions:
        wanted = {ext.lower().lstrip(".") for ext in extensions}
        files = [p for p in files
                 if os.path.splitext(p)[1].lower().lstrip(".") in wanted]
    return files


def replace_in_file(path, pattern, replacement, dry_run=False,
                    backup=False, encoding="utf-8"):
    """Apply the replacement to one file; return the replacement count."""
    with open(path, encoding=encoding, errors="strict") as handle:
        text = handle.read()
    new_text, count = pattern.subn(replacement, text)
    if count == 0:
        return 0
    if dry_run:
        return count
    if backup:
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding=encoding) as handle:
        handle.write(new_text)
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Bulk find-and-replace across many text files.")
    parser.add_argument("targets", nargs="+", metavar="FILE_OR_DIR",
                        help="files, folders, or glob patterns to process")
    parser.add_argument("--find", required=True,
                        help="text (or regex with --regex) to find")
    parser.add_argument("--replace", required=True,
                        help="replacement text")
    parser.add_argument("--regex", action="store_true",
                        help="treat --find as a regular expression")
    parser.add_argument("--ignore-case", action="store_true",
                        help="match without regard to case")
    parser.add_argument("--recursive", "-r", action="store_true",
                        help="recurse into subfolders")
    parser.add_argument("--extensions",
                        help="comma-separated extensions to process, "
                             "e.g. 'txt,md' (default: all files)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would change, without changing files")
    parser.add_argument("--backup", action="store_true",
                        help="save a .bak copy of each changed file")
    parser.add_argument("--encoding", default="utf-8",
                        help="file encoding (default: utf-8)")
    args = parser.parse_args(argv)

    extensions = [e.strip() for e in args.extensions.split(",")] \
        if args.extensions else None
    files = collect_files(args.targets, recursive=args.recursive,
                          extensions=extensions)
    if not files:
        print("error: no files matched", file=sys.stderr)
        return 1

    flags = re.IGNORECASE if args.ignore_case else 0
    search = args.find if args.regex else re.escape(args.find)
    try:
        pattern = re.compile(search, flags)
    except re.error as exc:
        print(f"error: invalid regex: {exc}", file=sys.stderr)
        return 1

    total_files, total_replacements = 0, 0
    for path in files:
        try:
            count = replace_in_file(path, pattern, args.replace,
                                    dry_run=args.dry_run, backup=args.backup,
                                    encoding=args.encoding)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"  skip {path}: {exc}", file=sys.stderr)
            continue
        if count:
            total_files += 1
            total_replacements += count
            verb = "would replace" if args.dry_run else "replaced"
            print(f"  {verb} {count} occurrence(s) in {path}")
    print(f"Done: {total_replacements} replacement(s) in {total_files} "
          f"file(s) out of {len(files)} checked"
          + (" (dry run, nothing changed)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
