"""Exercise publication boundaries and the failure behavior of release switching."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_site import NOTES, ROOT, build_site, validate_site
from update_site import publish, update


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / ".site-tests")
        self.workspace = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_selected_notes_and_links(self):
        output = self.workspace / "site"
        report = build_site(ROOT, output, "test-revision")
        self.assertEqual(report["pages"], 20)
        self.assertEqual(report["files"], sum(p.is_file() for p in output.rglob("*")))
        self.assertFalse((output / "notes/李沐-动手学深度学习").exists())
        self.assertFalse((output / ".git").exists())
        lesson = (output / "lessons/0001-array-shapes.html").read_text(encoding="utf-8")
        self.assertNotIn(".md\"", lesson)
        self.assertIn(".pdf#page=39", lesson)
        note = (output / NOTES / "00-学习导航.html").read_text(encoding="utf-8")
        self.assertIn("/blob/main/NOTES.md", note)
        self.assertIn("/tree/main/mycode/", note)
        math = (output / NOTES / "03-神经网络.html").read_text(encoding="utf-8")
        self.assertIn('class="arithmatex"', math)
        self.assertIn("<table>", math)
        self.assertIn("<pre><code", math)
        self.assertTrue((output / "assets/vendor/mathjax/tex-svg-full.js").is_file())
        self.assertTrue((output / "mycode/chapter3.ipynb").is_file())
        chapter5 = (output / "reference/chapter5.html").read_text(encoding="utf-8")
        self.assertIn("05-%E8%AF%AF%E5%B7%AE%E5%8F%8D%E5%90%91%E4%BC%A0%E6%92%AD%E6%B3%95.html", chapter5)
        self.assertTrue((output / "assets/chapter5-accuracy.svg").is_file())
        self.assertTrue((output / NOTES / "05-误差反向传播法.html").is_file())
        self.assertTrue((output / "lessons/0009-backprop-review.html").is_file())

    def test_missing_resource_fails_validation(self):
        output = self.workspace / "broken"
        output.mkdir()
        (output / "index.html").write_text('<img src="missing.png">', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing.png"):
            validate_site(output)

    def test_same_revision_skips_build(self):
        base = self.workspace
        (base / "current").mkdir()
        (base / "current/build.json").write_text(json.dumps({"revision": "abc"}), encoding="utf-8")
        with patch("update_site.subprocess.check_output", return_value="abc\n"), patch("update_site.run") as command, patch("update_site.publish") as build:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertIsNone(update(base, ROOT, pull=False))
            command.assert_not_called()
            build.assert_not_called()

    def test_failed_build_preserves_current(self):
        base = self.workspace
        current = base / "current"
        current.mkdir()
        sentinel = current / "index.html"
        sentinel.write_text("old site", encoding="utf-8")
        with patch("update_site.run", side_effect=subprocess.CalledProcessError(1, "builder")):
            with self.assertRaises(subprocess.CalledProcessError):
                publish(base, ROOT, "failed-revision")
        self.assertEqual(sentinel.read_text(), "old site")
        self.assertEqual(list((base / "releases").iterdir()), [])

    @unittest.skipIf(sys.platform == "win32", "Symlink publication is verified on the Linux deployment host")
    def test_release_switch_and_previous_retention(self):
        base = self.workspace

        def builder(*args, **kwargs):
            destination = Path(args[args.index("--output") + 1])
            (destination / "build.json").write_text("{}")

        with patch("update_site.run", side_effect=builder):
            first = publish(base, ROOT, "first")
            second = publish(base, ROOT, "second")
            third = publish(base, ROOT, "third")
        self.assertEqual((base / "current").resolve(), third)
        self.assertEqual((base / "previous").resolve(), second)
        self.assertFalse(first.exists())
        self.assertEqual(third.stat().st_mode & 0o777, 0o755)


if __name__ == "__main__":
    (ROOT / ".site-tests").mkdir(exist_ok=True)
    unittest.main()
