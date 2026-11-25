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


if __name__ == "__main__":
    unittest.main()
