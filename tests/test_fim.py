import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


FIM = Path(__file__).resolve().parents[1] / "fim.py"


def run_fim(*arguments):
    return subprocess.run(
        [sys.executable, str(FIM), *arguments],
        capture_output=True,
        text=True,
    )


class FileIntegrityTests(unittest.TestCase):

    def test_single_file_change(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "test.txt"
            target.write_text("original\n", encoding="utf-8")

            self.assertEqual(run_fim("create", str(target)).returncode, 0)
            self.assertEqual(run_fim("check", str(target)).returncode, 0)

            target.write_text("changed\n", encoding="utf-8")
            self.assertEqual(run_fim("check", str(target)).returncode, 1)

    def test_directory_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            first = folder / "first.txt"
            second = folder / "second.txt"

            first.write_text("one\n", encoding="utf-8")
            second.write_text("two\n", encoding="utf-8")

            self.assertEqual(run_fim("create", str(folder)).returncode, 0)
            self.assertEqual(run_fim("check", str(folder)).returncode, 0)

            first.write_text("modified\n", encoding="utf-8")
            second.unlink()
            (folder / "new.txt").write_text("new\n", encoding="utf-8")

            result = run_fim("check", str(folder))
            self.assertEqual(result.returncode, 1)
            self.assertIn("[ADDED]", result.stdout)
            self.assertIn("[MODIFIED]", result.stdout)
            self.assertIn("[DELETED]", result.stdout)


if __name__ == "__main__":
    unittest.main()
