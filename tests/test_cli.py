import json
import os
import tempfile
import unittest

from receipt_check.__main__ import main

H = "e" * 40


class TestCli(unittest.TestCase):
    def write(self, data):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))
        self.addCleanup(os.remove, path)
        return path

    def test_eligible(self):
        p = self.write([{"text": "SHIP", "sha": H, "family": "openai"}, {"text": "SHIP", "sha": H, "family": "xai"}])
        self.assertEqual(main([p, H, "anthropic"]), 0)

    def test_not_eligible(self):
        p = self.write([{"text": "SHIP", "sha": H, "family": "openai"}])
        self.assertEqual(main([p, H, "anthropic"]), 1)

    def test_bad_json(self):
        self.assertEqual(main([self.write("{not json"), H, "anthropic"]), 2)

    def test_not_a_list(self):
        self.assertEqual(main([self.write({"a": 1}), H, "anthropic"]), 2)

    def test_wrong_arg_count(self):
        self.assertEqual(main([H]), 2)

    def test_malformed_receipt(self):
        for item in ("SHIP", {"text": 1, "sha": H}, {"text": "SHIP", "sha": H, "family": ["xai"]}):
            with self.subTest(item=item):
                self.assertEqual(main([self.write([item]), H, "anthropic"]), 2)

    def test_deeply_nested_json(self):
        p = self.write("[" * 100000 + "]" * 100000)
        self.assertEqual(main([p, H, "anthropic"]), 2)

    def test_blank_author_family(self):
        p = self.write([])
        for family in ("", "  "):
            with self.subTest(family=family):
                self.assertEqual(main([p, H, family]), 2)

    def test_bad_head_sha(self):
        p = self.write([])
        for head in ("e" * 7, "E" * 40):
            with self.subTest(head=head):
                self.assertEqual(main([p, head, "anthropic"]), 2)


if __name__ == "__main__":
    unittest.main()
