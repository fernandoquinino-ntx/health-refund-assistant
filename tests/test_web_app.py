import unittest

from health_refund_assistant import web_app


class WebAppTests(unittest.TestCase):
    def test_prompt_selector_discovers_versions_in_numerical_order(self):
        extraction_versions = web_app.prompt_versions(
            web_app.PROMPTS_DIR / "vlm_extractor"
        )
        assistant_versions = web_app.prompt_versions(
            web_app.ASSISTANT_PROMPTS_DIR
        )

        self.assertEqual(
            extraction_versions,
            ["v1.0", "v1.1", "v2.0", "v3.0", "v4.0"],
        )
        self.assertEqual(assistant_versions, ["v1.0"])


if __name__ == "__main__":
    unittest.main()
