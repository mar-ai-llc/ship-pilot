import unittest

from receipt_check.verdict import parse_verdict, verdict_for_head

H = "c" * 40


def receipt(line):
    return "# PR #12 independent review\n\n" + line + "\n\nExecutor: test\n"


class TestVerdict(unittest.TestCase):
    def test_ship_at_full_head(self):
        self.assertEqual(verdict_for_head(receipt("VERDICT: SOURCE SHIP at exact `%s`." % H), H), "SHIP")

    def test_block_at_full_head(self):
        self.assertEqual(verdict_for_head(receipt("VERDICT: BLOCK at exact `%s`." % H), H), "BLOCK")

    def test_other_head_is_no_vote(self):
        self.assertEqual(verdict_for_head(receipt("VERDICT: SOURCE SHIP at exact `%s`." % ("d" * 40)), H), "NO_VOTE")

    def test_missing_line_is_no_vote(self):
        self.assertEqual(parse_verdict("looks good"), ("NO_VOTE", None))


if __name__ == "__main__":
    unittest.main()
