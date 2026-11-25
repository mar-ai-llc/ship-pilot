"""Command line: python3 -m receipt_check RECEIPTS.json HEAD_SHA AUTHOR_FAMILY

RECEIPTS.json is a list of {"text", "sha", "family"} objects (synthetic data).
Prints ELIGIBLE or NOT ELIGIBLE. Exit codes: 0 eligible, 1 not eligible,
2 bad input (unreadable file, not a JSON list, wrong argument count).
"""
import json
import sys

from .core import eligible


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    path, head, family = argv
    try:
        with open(path) as f:
            receipts = json.load(f)
    except (OSError, ValueError) as e:
        print(f"bad input: {e}", file=sys.stderr)
        return 2
    if not isinstance(receipts, list):
        print("bad input: receipts must be a JSON list", file=sys.stderr)
        return 2
    ok = eligible(receipts, head, family)
    print("ELIGIBLE" if ok else "NOT ELIGIBLE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
