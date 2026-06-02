import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.analyzer import analyze_project
from envlens.report import render_doctor, render_sarif, render_summary


class ReportTests(unittest.TestCase):
    def test_renders_sarif_summary_and_doctor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".env").write_text("", encoding="utf-8")
            (root / ".env.example").write_text("DATABASE_URL=postgres://localhost/db\n", encoding="utf-8")

            analysis = analyze_project(root, scan_code=False)
            sarif = json.loads(render_sarif(analysis))

            self.assertEqual(sarif["version"], "2.1.0")
            self.assertTrue(sarif["runs"][0]["results"])
            self.assertIn("Errors", render_summary(analysis))
            self.assertIn("Recommended fixes", render_doctor(analysis))


if __name__ == "__main__":
    unittest.main()

