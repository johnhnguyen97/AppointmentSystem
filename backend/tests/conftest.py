"""Configure pytest with HTML reporting."""
import pytest
from pathlib import Path

def pytest_html_report_title(report):
    """Customize the HTML report title."""
    report.title = "Test Results"

def pytest_configure(config):
    """Set up HTML report configuration."""
    # Define environment
    config._metadata = {
        'Project': 'Appointment System',
        'Environment': 'Test'
    }

    assets_path = Path(__file__).parent / "assets"

    # Configure HTML report
    config.option.self_contained_html = True
    config.option.html_show_source = False

    # Set CSS directly from file content
    css_path = assets_path / "custom_style.css"
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            config.option.css = f.read()

    # Set logo if available
    logo_path = assets_path / "color_logo.svg"
    if logo_path.exists():
        config.option.html_report_logo = str(logo_path.absolute())

def pytest_html_results_table_header(cells):
    """Add custom columns to the results table."""
    cells.insert(2, "<th>Description</th>")
    cells.pop() # Remove links column

def pytest_html_results_table_row(report, cells):
    """Add values for custom columns."""
    cells.insert(2, f'<td>{getattr(report, "description", "")}</td>')
    cells.pop() # Remove links column

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add metadata and description to test reports."""
    outcome = yield
    report = outcome.get_result()

    # Add test docstring as description
    doc = str(item.function.__doc__ or '')
    report.description = doc.strip()

    # Add test category if available
    category = item.get_closest_marker('category')
    if category:
        report.category = category.name
