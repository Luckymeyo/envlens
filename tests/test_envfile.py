import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.envfile import parse_env_file


class EnvFileTests(unittest.TestCase):
    def test_parse_quotes_comments_and_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / ".env"
            path.write_text(
                "\n".join(
                    [
                        "DATABASE_URL='postgres://localhost/db'",
                        "PORT=3000 # local port",
                        "export DEBUG=true",
                        "PORT=4000",
                    ]
                ),
                encoding="utf-8",
            )

            parsed = parse_env_file(path)

            self.assertEqual(parsed.entries["DATABASE_URL"].value, "postgres://localhost/db")
            self.assertEqual(parsed.entries["PORT"].value, "4000")
            self.assertEqual(parsed.entries["DEBUG"].value, "true")
            self.assertEqual(len(parsed.duplicates), 1)
            self.assertEqual(parsed.duplicates[0].key, "PORT")


if __name__ == "__main__":
    unittest.main()

