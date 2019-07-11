def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'vispy_app_test: Tests that require a valid GUI application.')
    warning_lines = """
    ignore:.*imp module.*:
    ignore:Using or importing the ABCs.*:
    """  # noqa: E501
    for warning_line in warning_lines.split('\n'):
        warning_line = warning_line.strip()
        if warning_line and not warning_line.startswith('#'):
            config.addinivalue_line('filterwarnings', warning_line)
