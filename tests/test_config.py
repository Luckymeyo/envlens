import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.config import load_config


class ConfigTests(unittest.TestCase):
    def test_loads_tool_envlens_config(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "pyproject.toml").write_text(
                "\n".join(
                    [
                        "[tool.envlens]",
                        'env = [".env.local", ".env.test"]',
                        'example = ".env.sample"',
                        'schema = "schema/env.yml"',
                        'preset = ["nextjs", "docker-compose"]',
                        'ignore = ["EXTERNAL_ONLY"]',
                        'format = "sarif"',
                        "strict = true",
                        "no_scan = true",
                        "summary = true",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_config(root)

            self.assertEqual(config.env_paths, [".env.local", ".env.test"])
            self.assertEqual(config.example_path, ".env.sample")
            self.assertEqual(config.schema_path, "schema/env.yml")
            self.assertEqual(config.presets, ["nextjs", "docker-compose"])
            self.assertEqual(config.ignore_keys, ["EXTERNAL_ONLY"])
            self.assertEqual(config.output_format, "sarif")
            self.assertTrue(config.strict)
            self.assertTrue(config.no_scan)
            self.assertTrue(config.summary)


if __name__ == "__main__":
    unittest.main()

