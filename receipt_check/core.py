"""Toy review-receipt checker for the ship-pilot repo. Synthetic data only."""
import re

_SHA = re.compile(r"^[0-9a-f]{40}$")


def is_full_sha(value):
    """True only for a full 40-character lowercase hex commit SHA."""
    return bool(_SHA.match(value or ""))


def classify(text):
    """Return SHIP, BLOCK or NO_VOTE from the first line of a receipt."""
    first = (text or "").strip().splitlines()[0:1]
    head = first[0].strip().upper() if first else ""
    if head.startswith("SOURCE_SHIP") or head.startswith("SHIP"):
        return "SHIP"
    if head.startswith("SOURCE_BLOCK") or head.startswith("BLOCK"):
        return "BLOCK"
    return "NO_VOTE"


def eligible(receipts, head_sha, author_family):
    """receipts: list of dicts {text, sha, family}. Needs 2 SHIPs from distinct
    non-author families at the exact full head SHA, and no BLOCK at that SHA."""
    if not is_full_sha(head_sha) or not receipts:
        return False
    at_head = [r for r in receipts if r.get("sha") == head_sha]
    if any(classify(r.get("text")) == "BLOCK" for r in at_head):
        return False
    families = {
        r.get("family")
        for r in at_head
        if classify(r.get("text")) == "SHIP" and r.get("family") and r.get("family") != author_family
    }
    return len(families) >= 2
