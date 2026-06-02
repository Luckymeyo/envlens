import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from envlens.analyzer import analyze_project


class AnalyzerTests(unittest.TestCase):
    def test_detects_contract_drift_and_type_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".env").write_text(
                "\n".join(
                    [
                        "DATABASE_URL=not-a-url",
                        "PORT=abc",
                        "UNTRACKED=value",
                    ]
                ),
                encoding="utf-8",
            )
            (root / ".env.example").write_text(
                "\n".join(
                    [
                        "DATABASE_URL=postgres://localhost/db",
                        "PORT=3000",
                        "SECRET_KEY=fake_secret_value_1234567890abcdef",
                        "STALE_FLAG=false",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "env.schema.yml").write_text(
                "\n".join(
                    [
                        "DATABASE_URL:",
                        "  type: url",
                        "PORT:",
                        "  type: integer",
                        "SECRET_KEY:",
                        "  type: string",
                        "  secret: true",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "app.py").write_text(
                'import os\nos.environ["DATABASE_URL"]\nos.getenv("MISSING_FROM_EXAMPLE")\n',
                encoding="utf-8",
            )

            analysis = analyze_project(root)
            codes = {issue.code for issue in analysis.issues}

            self.assertIn("type-mismatch", codes)
            self.assertIn("missing-in-example", codes)
            self.assertIn("missing-in-env", codes)
            self.assertIn("undocumented-env", codes)
            self.assertIn("secret-in-example", codes)

    def test_relative_env_paths_prefer_project_root_over_parent_cwd(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            project = workspace / "project"
            project.mkdir()
            (workspace / ".env").write_text("ROOT_ONLY=value\n", encoding="utf-8")
            (project / ".env").write_text("PROJECT_KEY=value\n", encoding="utf-8")
            (project / ".env.example").write_text("PROJECT_KEY=value\n", encoding="utf-8")
            (project / "app.py").write_text('import os\nos.getenv("PROJECT_KEY")\n', encoding="utf-8")

            old_cwd = Path.cwd()
            try:
                import os

                os.chdir(workspace)
                analysis = analyze_project(project, env_paths=[".env"])
            finally:
                os.chdir(old_cwd)

            self.assertFalse(analysis.issues)

    def test_presets_document_framework_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".env").write_text("", encoding="utf-8")
            (root / ".env.example").write_text("", encoding="utf-8")
            (root / "app.ts").write_text("const mode = import.meta.env.MODE;\n", encoding="utf-8")

            analysis = analyze_project(root, preset_names=["vite"])

            self.assertNotIn("missing-in-example", {issue.code for issue in analysis.issues})


if __name__ == "__main__":
    unittest.main()
