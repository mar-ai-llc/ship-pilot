"""Command line: python3 -m receipt_check RECEIPTS.json HEAD_SHA AUTHOR_FAMILY

RECEIPTS.json is a list of {"text", "sha", "family"} objects (synthetic data).
Prints ELIGIBLE or NOT ELIGIBLE. Exit codes: 0 eligible, 1 not eligible,
2 bad input (unreadable file, not a JSON list of objects, a text, sha or family
that is not a string or null, HEAD_SHA not a full lowercase SHA, blank
AUTHOR_FAMILY, wrong argument count).
"""
import json
import sys

from .core import eligible, is_full_sha


def _is_receipt(item):
    return isinstance(item, dict) and all(
        item.get(key) is None or isinstance(item.get(key), str)
        for key in ("text", "sha", "family")
    )


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    path, head, family = argv
    if not is_full_sha(head):
        print("bad input: HEAD_SHA must be a full lowercase SHA", file=sys.stderr)
        return 2
    if not family.strip():
        print("bad input: AUTHOR_FAMILY must not be blank", file=sys.stderr)
        return 2
    try:
        with open(path, encoding="utf-8") as f:
            receipts = json.load(f)
    except (OSError, ValueError, RecursionError) as e:
        print(f"bad input: {e}", file=sys.stderr)
        return 2
    if not isinstance(receipts, list) or not all(map(_is_receipt, receipts)):
        print("bad input: receipts must be a JSON list of receipt objects", file=sys.stderr)
        return 2
    ok = eligible(receipts, head, family)
    print("ELIGIBLE" if ok else "NOT ELIGIBLE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
