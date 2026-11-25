import unittest

from receipt_check import classify, eligible, is_full_sha

H = "a" * 40


def r(text, family, sha=H):
    return {"text": text, "family": family, "sha": sha}


class TestReceipts(unittest.TestCase):
    def test_full_sha(self):
        self.assertTrue(is_full_sha(H))
        self.assertFalse(is_full_sha("a" * 7))
        self.assertFalse(is_full_sha("A" * 40))
        self.assertFalse(is_full_sha(None))

    def test_classify(self):
        self.assertEqual(classify("SOURCE_SHIP abc"), "SHIP")
        self.assertEqual(classify("SOURCE_BLOCK abc"), "BLOCK")
        self.assertEqual(classify("looks fine to me"), "NO_VOTE")
        self.assertEqual(classify(""), "NO_VOTE")

    def test_two_independent_ships(self):
        self.assertTrue(eligible([r("SHIP", "openai"), r("SHIP", "xai")], H, "anthropic"))

    def test_author_vote_does_not_count(self):
        self.assertFalse(eligible([r("SHIP", "anthropic"), r("SHIP", "xai")], H, "anthropic"))

    def test_same_family_twice_is_one_vote(self):
        self.assertFalse(eligible([r("SHIP", "xai"), r("SHIP", "xai")], H, "anthropic"))

    def test_block_at_head_wins(self):
        self.assertFalse(eligible([r("SHIP", "openai"), r("SHIP", "xai"), r("BLOCK", "google")], H, "anthropic"))

    def test_stale_sha_ignored(self):
        old = "b" * 40
        self.assertFalse(eligible([r("SHIP", "openai", old), r("SHIP", "xai")], H, "anthropic"))

    def test_short_head_rejected(self):
        self.assertFalse(eligible([r("SHIP", "openai"), r("SHIP", "xai")], "a" * 7, "anthropic"))

    def test_empty_list(self):
        self.assertFalse(eligible([], H, "anthropic"))


if __name__ == "__main__":
    unittest.main()
