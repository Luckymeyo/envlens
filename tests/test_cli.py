import json
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.cli import main
from envlens.schema_json import ENV_SCHEMA_JSON


class CliTests(unittest.TestCase):
    def test_list_presets_json(self):
        buffer = StringIO()
        with patch("sys.stdout", buffer):
            code = main(["list-presets", "--format", "json"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertIn("nextjs", payload)
        self.assertIn("vite", payload)

    def test_schema_command_prints_env_schema_json(self):
        buffer = StringIO()
        with patch("sys.stdout", buffer):
            code = main(["schema"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["$id"], ENV_SCHEMA_JSON["$id"])
        self.assertIn("envSpec", payload["$defs"])

    def test_committed_schema_file_matches_cli_schema(self):
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "env.schema.json"
        payload = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertEqual(payload, ENV_SCHEMA_JSON)


if __name__ == "__main__":
    unittest.main()
