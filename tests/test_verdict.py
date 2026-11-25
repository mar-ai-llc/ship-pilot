import unittest

from receipt_check.verdict import parse_verdict, verdict_for_head

H = "c" * 40


def receipt(line):
    return "# PR #12 independent review\n\n" + line + "\n\nExecutor: test\n"


def line(word, sha):
    return "VERDICT: SOURCE %s at exact `%s`." % (word, sha)


class TestVerdict(unittest.TestCase):
    def test_ship_at_full_head(self):
        self.assertEqual(verdict_for_head(receipt("VERDICT: SOURCE SHIP at exact `%s`." % H), H), "SHIP")

    def test_block_at_full_head(self):
        self.assertEqual(verdict_for_head(receipt("VERDICT: BLOCK at exact `%s`." % H), H), "BLOCK")

    def test_other_head_is_no_vote(self):
        self.assertEqual(verdict_for_head(receipt("VERDICT: SOURCE SHIP at exact `%s`." % ("d" * 40)), H), "NO_VOTE")

    def test_missing_line_is_no_vote(self):
        self.assertEqual(parse_verdict("looks good"), ("NO_VOTE", None))

    def test_short_sha_is_no_vote(self):
        for sha in ("c", "c" * 7, "c" * 39):
            self.assertEqual(verdict_for_head(receipt(line("SHIP", sha)), H), "NO_VOTE", sha)

    def test_malformed_sha_is_not_parsed(self):
        for sha in ("c" * 7, "c" * 41, "C" * 40):
            self.assertEqual(parse_verdict(receipt(line("SHIP", sha))), ("NO_VOTE", None), sha)

    def test_short_head_is_no_vote(self):
        self.assertEqual(verdict_for_head(receipt(line("SHIP", H)), "c" * 7), "NO_VOTE")

    def test_later_block_wins(self):
        text = receipt(line("SHIP", H) + "\n\n" + line("BLOCK", H))
        self.assertEqual(parse_verdict(text), ("BLOCK", H))
        self.assertEqual(verdict_for_head(text, H), "BLOCK")

    def test_later_ship_does_not_override_block(self):
        text = receipt(line("BLOCK", H) + "\n" + line("SHIP", H))
        self.assertEqual(verdict_for_head(text, H), "BLOCK")

    def test_block_at_head_after_stale_verdicts(self):
        for first in ("SHIP", "BLOCK"):
            text = receipt(line(first, "d" * 40) + "\n" + "note\n" * 8 + line("BLOCK", H))
            self.assertEqual(verdict_for_head(text, H), "BLOCK", first)

    def test_later_ship_does_not_count(self):
        text = receipt("Pending.\n\n" + line("SHIP", H))
        self.assertEqual(verdict_for_head(text, H), "NO_VOTE")

    def test_header_required(self):
        for text in (line("SHIP", H), "To approve, post:\n\n" + line("SHIP", H)):
            self.assertEqual(verdict_for_head(text, H), "NO_VOTE", text)

    def test_blank_line_after_header_required(self):
        text = "# PR #12 independent review\n" + line("SHIP", H) + "\nmore"
        self.assertEqual(verdict_for_head(text, H), "NO_VOTE")

    def test_indented_verdict_is_no_vote(self):
        for word in ("SHIP", "BLOCK"):
            text = receipt("    " + line(word, H))
            self.assertEqual(verdict_for_head(text, H), "NO_VOTE", word)

    def test_fenced_block_example_is_ignored(self):
        for opening, inner, closing in (("```", "", "```"), ("~~~", "", "~~~"), ("````", "```\n", "````")):
            example = opening + "\n" + inner + line("BLOCK", H) + "\n" + closing
            text = receipt(line("SHIP", H) + "\n\n" + example)
            self.assertEqual(verdict_for_head(text, H), "SHIP", opening)

    def test_block_after_closed_fence_counts(self):
        text = receipt(line("SHIP", H) + "\n```\ncode\n```\n" + line("BLOCK", H))
        self.assertEqual(verdict_for_head(text, H), "BLOCK")

    def test_loosely_written_block_wins(self):
        for block in (
            "VERDICT: BLOCK at exact `%s`. Tests fail." % H,
            "**VERDICT: BLOCK at exact `%s`.**" % H,
            "VERDICT: **BLOCK** at exact `%s`." % H,
            "VERDICT: SOURCE_BLOCK at exact `%s`." % H,
            "   " + line("BLOCK", H),
        ):
            text = receipt(line("SHIP", H) + "\n\n" + block)
            self.assertEqual(verdict_for_head(text, H), "BLOCK", block)

    def test_inline_backticks_do_not_open_a_fence(self):
        text = receipt(line("SHIP", H) + "\n```x``` is broken\n" + line("BLOCK", H))
        self.assertEqual(verdict_for_head(text, H), "BLOCK")

    def test_standalone_inline_code_line_does_not_hide_block(self):
        head = "f77befba41348bd37d43042896e24a083a4e25b0"
        text = "\n".join((
            "# PR #1 independent review",
            "",
            line("SHIP", head),
            "",
            "```example```",
            "",
            line("BLOCK", head),
        ))
        self.assertEqual(parse_verdict(text), ("BLOCK", head))
        self.assertEqual(verdict_for_head(text, head), "BLOCK")

    def test_block_in_unclosed_fence_counts(self):
        for before in ("- item\n  ```\n  code\n", "<!--\n```\n-->\n"):
            text = receipt(line("SHIP", H) + "\n" + before + line("BLOCK", H))
            self.assertEqual(verdict_for_head(text, H), "BLOCK", before)


if __name__ == "__main__":
    unittest.main()
