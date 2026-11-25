"""Parse the fleet review-receipt header (synthetic pilot data only).

Spec: a review receipt starts like this

    # PR #<n> independent review

    VERDICT: SOURCE SHIP at exact `<full 40-character head SHA>`.

parse_verdict(text) returns (verdict, sha) where verdict is SHIP, BLOCK or
NO_VOTE. A verdict only counts when the SHA is a full 40-character lowercase
hex commit SHA (short SHAs never count). verdict_for_head(text, head_sha)
returns the verdict only when it names exactly head_sha, else NO_VOTE.

The header must be the first line, followed by a blank line and then the
VERDICT line, unindented. A SHIP counts only from that position. A BLOCK also
counts from any later line outside a closed code fence, and wins over a SHIP.
A BLOCK is matched loosely, so that a veto is not lost to formatting: up to
three leading spaces, bold or italic markers, SOURCE_BLOCK and text after the
SHA are all accepted.
"""
import re

_HEADER = re.compile(r"# PR #[0-9]+ independent review\s*")
_SHIP = re.compile(r"VERDICT:\s*(?:SOURCE )?SHIP\s+at\s+exact\s+`([0-9a-f]{40})`\.?\s*")
_BLOCK = re.compile(
    r" {0,3}[*_]*VERDICT[*_]*:[*_\s]*(?:SOURCE[ _])?BLOCK[*_]*\s+at\s+exact\s+`([0-9a-f]{40})`.*"
)
_FENCE = re.compile(r" {0,3}(`{3,}(?=[^`]*$)|~{3,})(.*)")


def _verdicts(text):
    """Return the (verdict, sha) pairs that count, in document order."""
    lines = (text or "").splitlines()
    if len(lines) < 3 or not _HEADER.fullmatch(lines[0]) or lines[1].strip():
        return []
    found = []
    fence = None  # the marker that opened the current code fence
    fenced = []  # BLOCKs inside it, dropped only if it closes
    for index, line in enumerate(lines[2:], start=2):
        marker = _FENCE.fullmatch(line)
        block = _BLOCK.fullmatch(line)
        if fence:
            if marker and marker.group(1).startswith(fence) and not marker.group(2).strip():
                fence = None
                fenced = []
            elif block:
                fenced.append(("BLOCK", block.group(1)))
        elif marker:
            fence = marker.group(1)
        elif block:
            found.append(("BLOCK", block.group(1)))
        elif index == 2:
            ship = _SHIP.fullmatch(line)
            if ship:
                found.append(("SHIP", ship.group(1)))
    return found + fenced


def parse_verdict(text):
    found = _verdicts(text)
    for verdict, sha in found:
        if verdict == "BLOCK":
            return verdict, sha
    return found[0] if found else ("NO_VOTE", None)


def verdict_for_head(text, head_sha):
    at_head = {verdict for verdict, sha in _verdicts(text) if sha == head_sha}
    for verdict in ("BLOCK", "SHIP"):
        if verdict in at_head:
            return verdict
    return "NO_VOTE"
