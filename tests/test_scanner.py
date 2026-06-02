import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.scanner import scan_project


class ScannerTests(unittest.TestCase):
    def test_scans_common_language_patterns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "app.py").write_text('import os\nos.getenv("DATABASE_URL")\n', encoding="utf-8")
            (root / "app.ts").write_text(
                'process.env.NODE_ENV\nimport.meta.env.PUBLIC_API_URL\n',
                encoding="utf-8",
            )
            (root / "main.go").write_text('os.Getenv("PORT")\n', encoding="utf-8")

            keys = {usage.key for usage in scan_project(root)}

            self.assertEqual(keys, {"DATABASE_URL", "NODE_ENV", "PUBLIC_API_URL", "PORT"})

    def test_python_expression_includes_closing_call(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "app.py").write_text('import os\nos.getenv("PORT", "3000")\n', encoding="utf-8")

            usages = scan_project(root)

            self.assertEqual(usages[0].expression, 'os.getenv("PORT", "3000")')


if __name__ == "__main__":
    unittest.main()
