"""Unit tests for reusable helper logic."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Instagram.instagram_downloader import build_target_stem, extract_shortcode
from common import functions as func


class TestCommonFunctions(unittest.TestCase):
    def test_sanitize_filename_replaces_invalid_chars(self) -> None:
        self.assertEqual(
            func.sanitize_filename('bad:/\\*?"<>|name'),
            "bad_name",
        )

    def test_extract_shortcode_from_instagram_url(self) -> None:
        shortcode = extract_shortcode("https://www.instagram.com/p/CxYZ123abcD/")
        self.assertEqual(shortcode, "CxYZ123abcD")

    def test_build_target_stem_returns_unique_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_file = os.path.join(temp_dir, "sample.mp4")
            with open(existing_file, "w", encoding="utf-8") as file_obj:
                file_obj.write("x")

            stem = build_target_stem(temp_dir, "sample", "fallback", ".mp4")
            self.assertTrue(stem.endswith("sample_1"))


if __name__ == "__main__":
    unittest.main()
