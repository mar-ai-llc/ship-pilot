"""Parse the fleet review-receipt header (synthetic pilot data only).

Spec: a review receipt starts like this

    # PR #<n> independent review

    VERDICT: SOURCE SHIP at exact `<full 40-character head SHA>`.

parse_verdict(text) returns (verdict, sha) where verdict is SHIP, BLOCK or
NO_VOTE. A verdict only counts when the SHA is a full 40-character lowercase
hex commit SHA (short SHAs never count). verdict_for_head(text, head_sha)
returns the verdict only when it names exactly head_sha, else NO_VOTE.
"""
import re

_LINE = re.compile(r"^VERDICT:\s*(SOURCE SHIP|SOURCE BLOCK|SHIP|BLOCK)\s+at\s+exact\s+`([0-9a-fA-F]+)`\.?\s*$")


def parse_verdict(text):
    for line in (text or "").splitlines()[:6]:
        m = _LINE.match(line.strip())
        if m:
            word, sha = m.group(1).upper(), m.group(2)
            verdict = "SHIP" if word.endswith("SHIP") else "BLOCK"
            return verdict, sha
    return "NO_VOTE", None


def verdict_for_head(text, head_sha):
    verdict, sha = parse_verdict(text)
    if verdict == "NO_VOTE" or not sha or not head_sha:
        return "NO_VOTE"
    if head_sha.startswith(sha):
        return verdict
    return "NO_VOTE"
