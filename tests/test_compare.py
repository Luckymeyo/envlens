import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.cli import main
from envlens.compare import compare_env_files, render_compare_json


class CompareTests(unittest.TestCase):
    def test_compare_detects_profile_drift_without_exposing_secret_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / ".env"
            target = root / ".env.production"
            schema = root / "env.schema.yml"
            base.write_text("DATABASE_URL=postgres://localhost:5432/app\nSECRET_KEY=local-placeholder\nPORT=3000\n", encoding="utf-8")
            target.write_text("DATABASE_URL=postgres://db.example.com:5432/app\nSECRET_KEY=production-placeholder\n", encoding="utf-8")
            schema.write_text(
                "\n".join(
                    [
                        "DATABASE_URL:",
                        "  type: url",
                        "  required: true",
                        "SECRET_KEY:",
                        "  type: string",
                        "  required: true",
                        "  secret: true",
                        "PORT:",
                        "  type: integer",
                        "  required: true",
                    ]
                ),
                encoding="utf-8",
            )

            comparison = compare_env_files(base, target, schema_path=schema, show_values=True)
            payload = json.loads(render_compare_json(comparison))

            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("value-drift", codes)
            self.assertIn("missing-required-target", codes)
            self.assertNotIn("missing-in-target", [finding["code"] for finding in payload["findings"] if finding["key"] == "PORT"])
            self.assertNotIn("production-placeholder", json.dumps(payload))

    def test_compare_cli_json_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / ".env"
            target = root / ".env.production"
            base.write_text("PORT=3000\n", encoding="utf-8")
            target.write_text("PORT=8000\n", encoding="utf-8")

            buffer = StringIO()
            with patch("sys.stdout", buffer):
                code = main(["compare", str(base), str(target), "--format", "json", "--show-values"])

            self.assertEqual(code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["summary"]["warnings"], 1)
            self.assertEqual(payload["findings"][0]["code"], "value-drift")


if __name__ == "__main__":
    unittest.main()
