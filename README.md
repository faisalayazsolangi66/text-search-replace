# Text Search Replace

Bulk find-and-replace across many text files. Give files, folders
or glob patterns, and every occurrence of `--find` is replaced
with `--replace`. Supports regular expressions (`--regex`),
case-insensitive matching (`--ignore-case`), recursion (`-r`),
an extension filter (`--extensions txt,md`), a preview mode
(`--dry-run`), and `.bak` backups (`--backup`).

## Requirements

- Python 3 (standard library only, no extra packages)

## Usage

```bash
python3 main.py notes.txt --find "colour" --replace "color"
python3 main.py docs/ -r --extensions md --find "TODO" --replace "DONE" --dry-run
python3 main.py "*.txt" --find "2025" --replace "2026" --backup
```

## Example

```bash
$ cat note.txt
The colour of the sky is blue.

$ python3 main.py note.txt --find "colour" --replace "color"
  replaced 1 occurrence(s) in /tmp/note.txt
Done: 1 replacement(s) in 1 file(s) out of 1 checked

$ cat note.txt
The color of the sky is blue.
```

## License

MIT — see [LICENSE](LICENSE).
