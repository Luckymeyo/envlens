import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class WebAssetTests(unittest.TestCase):
    def test_static_web_entry_references_existing_local_assets(self):
        root = Path(__file__).resolve().parents[1]
        index = root / "web" / "index.html"
        html = index.read_text(encoding="utf-8")

        for asset in ["styles.css", "app.js", "assets/envlens-mark.svg"]:
            self.assertIn(asset, html)
            self.assertTrue((root / "web" / asset).exists(), asset)

    def test_static_web_entry_includes_workbench_views(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "web" / "index.html").read_text(encoding="utf-8")

        for view in [
            "issues",
            "radar",
            "secrets",
            "variables",
            "profiles",
            "policy",
            "timeline",
            "explain",
            "fixplan",
            "schema",
            "share",
            "docs",
            "export",
            "cli",
        ]:
            self.assertIn(f'id="view-{view}"', html)

        for control in [
            "profileInput",
            "ignoreKeys",
            "themeToggle",
            "shareState",
            "riskRadar",
            "secretAuditBody",
            "policyErrorLimit",
            "historyBody",
            "shareOutput",
            "schemaOutput",
            "cliOutput",
        ]:
            self.assertIn(f'id="{control}"', html)

    def test_static_web_app_includes_major_feature_renderers(self):
        root = Path(__file__).resolve().parents[1]
        app = (root / "web" / "app.js").read_text(encoding="utf-8")

        for renderer in [
            "renderRadar",
            "renderSecrets",
            "renderPolicy",
            "renderTimeline",
            "renderShare",
            "buildSecretAudit",
            "buildRiskRadar",
        ]:
            self.assertIn(f"function {renderer}", app)

    def test_static_web_app_avoids_remote_runtime_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "web" / "index.html").read_text(encoding="utf-8")
        scripts = re.findall(r"<script[^>]+src=\"([^\"]+)\"", html)
        stylesheets = re.findall(r"<link[^>]+href=\"([^\"]+)\"", html)

        remote_assets = [asset for asset in [*scripts, *stylesheets] if asset.startswith(("http://", "https://"))]
        self.assertEqual(remote_assets, [])


if __name__ == "__main__":
    unittest.main()
