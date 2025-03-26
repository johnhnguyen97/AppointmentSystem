"""Root conftest.py for test configuration and HTML reporting with logo."""
import os
import sys
import pytest
from datetime import datetime
from pathlib import Path

from pytest_html import extras

def pytest_html_report_title(report):
    """Set the title for the HTML report."""
    report.title = "Appointment System Test Report"

def pytest_configure(config):
    """Configure test metadata and custom CSS."""
    # Fix the metadata configuration
    # Get Python version directly from sys module
    # Get pytest version directly from pytest
    config._metadata = {
        'Project Name': 'Appointment System',
        'Environment': os.getenv('APP_ENV', 'Test'),
        'Python Version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'Pytest Version': pytest.__version__,
        'Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Force render_collapsed to boolean
    config._inicache['render_collapsed'] = False

    # Register markers
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "database: mark tests that require database")
    config.addinivalue_line("markers", "api: mark tests that require API")
    config.addinivalue_line("markers", "slow: mark tests as slow running")
    config.addinivalue_line("markers", "unit: mark tests as unit tests")
    config.addinivalue_line("markers", "e2e: mark tests as end-to-end tests")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add timing information and additional details to test report."""
    outcome = yield
    report = outcome.get_result()

    # Add test duration
    if hasattr(call, 'start') and hasattr(call, 'stop'):
        report.duration = call.stop - call.start

    # Add extra report sections
    if report.when == "call":
        # Initialize extras if not present
        report.extras = getattr(report, 'extras', [])

        # Add system info for database tests
        if "database" in item.keywords:
            report.extras.append(extras.html("<div class='database-info'>Database Tests</div>"))
            report.extras.append(
                extras.json({
                    "database": "PostgreSQL",
                    "connection": "Async",
                    "orm": "SQLAlchemy"
                }, name="Database Info")
            )

        # Remove the download links section as requested
        # since it might be causing issues

def pytest_html_results_table_header(cells):
    """Customize the results table header."""
    cells.insert(2, '<th class="sortable time" data-column-type="time">Time</th>')
    cells.insert(1, "<th>Description</th>")
    cells.pop()  # Remove links column which we'll handle differently

def pytest_html_results_table_row(report, cells):
    """Customize the results table rows."""
    cells.insert(2, f'<td class="col-time">{datetime.now().strftime("%H:%M:%S")}</td>')
    cells.insert(1, f'<td>{getattr(report, "description", "")}</td>')
    cells.pop()  # Remove links column which we'll handle differently

def pytest_html_results_table_html(report, data):
    """Add custom HTML to the report."""
    if report.passed:
        data.append("<div class='passed-marker'>✓</div>")
    elif report.failed:
        data.append("<div class='failed-marker'>✗</div>")

def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary information including logo."""
    # Add logo to the summary section
    logo_path = Path(__file__).parent / "tests/assets/color_logo.svg"
    if logo_path.exists():
        with open(logo_path, 'r') as f:
            svg_content = f.read()

        # Add custom CSS to position logo next to the title
        summary.append('''
        <style>
            /* Override the default h1 style */
            h1 {
                display: inline-flex !important;
                align-items: center !important;
                gap: 15px !important;
            }

            /* Style for the logo container */
            .report-logo {
                display: inline-block !important;
                width: 60px !important;
                height: auto !important;
                vertical-align: middle !important;
                margin-right: 10px !important;
            }

            /* Hide the duplicate logo in summary */
            .header-container .logo {
                display: none !important;
            }

            /* Fix for the title container */
            .title-container {
                display: flex !important;
                align-items: center !important;
                margin-top: 20px !important;
                margin-bottom: 20px !important;
            }
        </style>
        ''')

        # Create a container that includes both logo and title
        summary.append('<div class="title-container"></div>')

        # Inject JavaScript to move the logo next to the title
        summary.append('''
        <script>
            // Wait for the DOM to be fully loaded
            document.addEventListener('DOMContentLoaded', function() {
                // Get the main title element
                var title = document.querySelector('h1');
                if (title) {
                    // Create logo container
                    var logoDiv = document.createElement('div');
                    logoDiv.className = 'report-logo';
                    logoDiv.innerHTML = document.querySelector('.logo').innerHTML;

                    // Insert logo before the title text
                    title.insertBefore(logoDiv, title.firstChild);
                }
            });
        </script>
        ''')

        # Still keep the header container for the summary, but the logo will be hidden by CSS
        summary.append('<div class="header-container" style="display: flex; align-items: center; margin-bottom: 20px;">')
        summary.append(f'<div class="logo" style="width: 80px; height: auto; margin-right: 20px;">{svg_content}</div>')
        summary.append('<div class="title-section">')
        summary.append('<h2>Appointment System Test Results</h2>')
        summary.append(f'<p>Run Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
        summary.append('</div>')
        summary.append('</div>')
    else:
        # Fallback if logo not found
        summary.append('<div class="summary-info">')
        summary.append('<h2>Appointment System Test Results</h2>')
        summary.append(f'<p>Run Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
        summary.append('</div>')

@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary information to terminal output."""
    yield

    # Print summary info
    print("\nTest Run Summary")
    print("===============")
    print(f"Total: {len(terminalreporter.stats.get('passed', [])) + len(terminalreporter.stats.get('failed', [])) + len(terminalreporter.stats.get('skipped', []))}")
    print(f"Passed: {len(terminalreporter.stats.get('passed', []))}")
    print(f"Failed: {len(terminalreporter.stats.get('failed', []))}")
    print(f"Skipped: {len(terminalreporter.stats.get('skipped', []))}")
    print(f"Duration: {datetime.now().strftime('%H:%M:%S')}")
