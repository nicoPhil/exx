import os
from helpers import get_multiline_conf_app

async def test_on_init_multiline():
    async with get_multiline_conf_app().run_test() as pilot:
        app = pilot.app
        assert os.environ.get("TEST_VAR") == "test-value"
        assert os.environ.get("TEST_VAR2") == "test-value2"

        os.environ.pop("TEST_VAR")
        os.environ.pop("TEST_VAR2")


