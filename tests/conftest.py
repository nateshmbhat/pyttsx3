import os
import pytest

def pytest_collection_modifyitems(items):
    """Skip tests after `test_changing_volume` if in CI environment."""
    if "CI" not in os.environ:
        return  # Only apply this logic if in CI

    skip = False  # Flag to start skipping after `test_changing_volume`
    for item in items:
        if "test_changing_volume" in item.nodeid:
            skip = True
        elif skip:
            item.add_marker(pytest.mark.skip(reason="Skipping in CI environment after test_changing_volume"))