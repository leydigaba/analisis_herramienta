import os
import unittest
from pathlib import Path


class OpenRouterConfigTests(unittest.TestCase):
    def test_accepts_common_openrouter_key_names(self):
        for name in ["OPENROUTER_API_KEY", "MI_CHAT_DATOS", "ANTHROPIC_API_KEY"]:
            os.environ.pop(name, None)

        os.environ["MI_CHAT_DATOS"] = "sk-test-key"

        try:
            from proyecto_final.chat import get_openrouter_api_key

            self.assertEqual(get_openrouter_api_key(), "sk-test-key")
        finally:
            os.environ.pop("MI_CHAT_DATOS", None)


if __name__ == "__main__":
    unittest.main()
