"""
Pytest collection configuration for this repository.

Some files in the repo are operational scripts that happen to use `test_*`
function names for CLI/demo execution, but they are not pytest unit tests and
require runtime arguments/fixtures that are not provided by pytest.
"""

collect_ignore = [
    "pre_launch_test.py",
    "test_batch_prediction.py",
    "test_capacity.py",
    "test_client.py",
]

