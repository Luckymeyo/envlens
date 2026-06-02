import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.schema import load_schema


class SchemaTests(unittest.TestCase):
    def test_loads_simple_yaml_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "env.schema.yml"
            path.write_text(
                "\n".join(
                    [
                        "NODE_ENV:",
                        "  type: enum",
                        "  required: false",
                        "  values: [development, test, production]",
                        "  default: development",
                    ]
                ),
                encoding="utf-8",
            )

            schema = load_schema(path)

            self.assertTrue(schema.exists)
            self.assertEqual(schema.specs["NODE_ENV"].type, "enum")
            self.assertFalse(schema.specs["NODE_ENV"].required)
            self.assertEqual(schema.specs["NODE_ENV"].values, ["development", "test", "production"])


if __name__ == "__main__":
    unittest.main()

