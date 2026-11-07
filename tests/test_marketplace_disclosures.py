import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MarketplaceDisclosureTests(unittest.TestCase):
    def test_openai_cost_guidance_is_informational_not_checkout_steering(self):
        readme = (ROOT / "plugins/openai/README.md").read_text()
        self.assertNotIn("https://cloud.mobilerun.ai/billing", readme)
        self.assertIn("https://docs.mobilerun.ai/credits", readme)
        self.assertIn("account settings", readme.lower())

        manifest = json.loads((ROOT / "plugins/openai/plugin.json").read_text())
        cases = manifest["extensions"]["com.openai"]["review"]["test_cases"]
        self.assertEqual(len(cases["positive"]), 6)
        self.assertEqual(len(cases["negative"]), 4)
        texts = " ".join(case["expected_behavior"] for case in cases["negative"])
        self.assertIn("unrelated promotions", texts.lower())
        self.assertIn("upgrade", texts.lower())


    def test_cursor_readme_links_directly_to_privacy_and_terms(self):
        readme = (ROOT / "plugins/cursor/README.md").read_text()
        self.assertIn("https://cloud.mobilerun.ai/legal/privacy-policy", readme)
        self.assertIn("https://cloud.mobilerun.ai/legal/terms-of-service", readme)
