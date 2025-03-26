"""Test runner script for generating HTML reports with categorized test structure."""
import os
import sys
import subprocess
import venv
import webbrowser
import tempfile
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import base64

def ensure_venv():
    """Ensure virtual environment exists and is activated with dependencies."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)

        # Install poetry and dependencies
        print("Installing dependencies...")
        python_exe = get_python_executable()
        subprocess.run([python_exe, "-m", "pip", "install", "poetry"], check=True)
        subprocess.run([python_exe, "-m", "poetry", "install", "--with", "dev"], check=True)

    # Activate venv by modifying PATH and VIRTUAL_ENV
    venv_bin = venv_path / "Scripts" if sys.platform == "win32" else venv_path / "bin"
    os.environ["PATH"] = str(venv_bin) + os.pathsep + os.environ["PATH"]
    os.environ["VIRTUAL_ENV"] = str(venv_path)
    sys.path.insert(0, str(venv_bin))

def get_python_executable():
    """Get the correct Python executable path."""
    if sys.platform == "win32":
        return str(Path("venv/Scripts/python.exe"))
    return str(Path("venv/bin/python"))

def parse_args():
    """Parse command line arguments with support for nested test categories."""
    parser = argparse.ArgumentParser(description="Run tests with HTML reporting")
    parser.add_argument("-m", "--marker", help="Run tests with specific marker (e.g., database, api)")
    parser.add_argument("-k", "--keyword", help="Only run tests which match the given substring expression")
    parser.add_argument("-c", "--category", help="Run tests from a specific category folder (e.g., database, auth)")
    parser.add_argument("--browser", action="store_true", help="Open report in browser")
    parser.add_argument("--no-browser", action="store_true", help="Don't open report in browser")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    return parser.parse_args()

def ensure_css_file_exists():
    """Ensure the custom CSS file exists for HTML reports."""
    css_path = Path("tests/assets/custom_style.css")
    css_dir = css_path.parent

    if not css_dir.exists():
        css_dir.mkdir(parents=True, exist_ok=True)

    if not css_path.exists():
        # Create a basic CSS file with minimal styling to avoid parsing issues
        with open(css_path, "w") as f:
            f.write("""
/* Basic styling */
body { font-family: Arial, sans-serif; }
.passed { color: green; }
.failed { color: red; }
.skipped { color: orange; }
#results-table { width: 100%; border-collapse: collapse; }
#results-table th, #results-table td { padding: 8px; border: 1px solid #ddd; }
#results-table th { background-color: #f2f2f2; }
""")

    # Check if file is readable
    try:
        with open(css_path, "r") as f:
            css_content = f.read()
            print(f"CSS file exists with {len(css_content)} bytes at {css_path.absolute()}")
    except Exception as e:
        print(f"Warning: Could not read CSS file: {e}")

    return str(css_path.absolute())

def ensure_dependencies():
    """Ensure all required dependencies are installed."""
    try:
        # Check for pkg_resources (part of setuptools)
        try:
            import pkg_resources
            print("setuptools/pkg_resources is already installed")
        except ImportError:
            print("Installing setuptools which provides pkg_resources...")
            subprocess.run([get_python_executable(), "-m", "pip", "install", "setuptools"], check=True)

        # Check for pytest-html
        try:
            import pytest_html
            print("pytest-html is already installed")
        except ImportError:
            print("Installing pytest-html...")
            subprocess.run([get_python_executable(), "-m", "pip", "install", "pytest-html"], check=True)
    except Exception as e:
        print(f"Warning: Error ensuring dependencies: {e}")
        print("Continuing anyway...")

def encode_logo_as_base64():
    """Encode the logo SVG as base64 for embedding in HTML."""
    logo_path = Path("tests/assets/color_logo.svg")
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                logo_data = f.read()
                return base64.b64encode(logo_data).decode('utf-8')
        except Exception as e:
            print(f"Warning: Could not read logo file: {e}")
    return ""

def run_tests(*args):
    """Run pytest with HTML report generation."""
    try:
        # Ensure we're in the backend directory
        os.chdir(Path(__file__).parent)

        # Parse command line arguments
        cli_args = parse_args()

        # Create timestamped report directory
        timestamp = datetime.now().strftime("%Y-%m/%d/%H%M%S")
        report_dir = Path("test-reports") / timestamp
        if cli_args.category:
            report_dir = report_dir / cli_args.category
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "report.html"

        # Build pytest command - completely stripped down to just the essentials
        pytest_cmd = [
            get_python_executable(),
            "-m",
            "pytest",
            "-v",                            # verbose output
            "--capture=sys",                 # capture stdout/stderr
            "--tb=short",                    # shorter traceback format
        ]

        # Add coverage if requested
        if cli_args.coverage:
            pytest_cmd.extend(["--cov=src", "--cov-report=term"])

        # Handle category-specific folder testing
        if cli_args.category:
            # Run only the tests in the specific category folder
            category_path = Path("tests") / cli_args.category
            if category_path.exists():
                pytest_cmd.append(str(category_path))
            else:
                print(f"Warning: Category directory '{category_path}' does not exist")
                pytest_cmd.append("tests/")
        else:
            # Run all tests
            pytest_cmd.append("tests/")

        # Add specific markers if provided
        if cli_args.marker:
            pytest_cmd.extend(["-m", cli_args.marker])

        # Add keyword filter if provided
        if cli_args.keyword:
            pytest_cmd.extend(["-k", cli_args.keyword])

        # Add any additional arguments from original function call
        if args:
            pytest_cmd.extend(args)

        # Print the command to help debug any issues
        cmd_str = " ".join(pytest_cmd)
        print(f"Running tests with command: {cmd_str}")

        # Set PYTHONPATH to include current directory and src directory
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{os.getcwd()};{os.path.join(os.getcwd(), 'src')}"

        # Remove ANY pytest-html related environment variables
        env_vars_to_remove = []
        for var in env:
            if "PYTEST_HTML" in var or "CSS" in var or "HTML" in var:
                env_vars_to_remove.append(var)

        for var in env_vars_to_remove:
            if var in env:
                del env[var]
                print(f"Removed environment variable: {var}")

        print(f"Report will be generated at: {report_path}")

        # Run pytest
        result = subprocess.run(
            pytest_cmd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent)  # Ensure we're in the correct directory
        )

        # Generate HTML report separately after tests run to avoid CSS issues
        if True:  # Always generate the report as long as the command ran
            print("Generating HTML report...")
            # Extract test status information
            test_status = "Unknown"
            if "FAILED" in result.stdout:
                test_status = "Failed"
            elif "PASSED" in result.stdout:
                test_status = "Passed"
            elif result.returncode != 0:
                test_status = "Error"

            # Process test results to extract individual test data with enhanced parsing
            tests = []
            all_lines = result.stdout.splitlines()

            # Enhanced test parsing logic with focus on db connection errors and multi-level exceptions
            i = 0
            test_blocks = []
            current_block = {"lines": [], "start_line": 0, "is_test": False}
            in_failures_section = False

            # Add markers to help parse pytest output patterns
            exception_markers = [
                "E       ",
                "ERROR",
                "FAILED",
                "Failed:",
                "AssertionError",
                "AttributeError",
            ]
            log_markers = ["Captured log call", "Captured stdout", "Captured stderr"]

            while i < len(all_lines):
                line = all_lines[i].strip()

                # Detect the FAILURES section header
                if line.startswith("=") and "FAILURES" in line:
                    in_failures_section = True

                    # Save the previous block if it exists
                    if current_block["lines"]:
                        test_blocks.append(current_block)

                    # Start a new block for failures section header
                    current_block = {
                        "lines": [all_lines[i]],
                        "start_line": i,
                        "is_test": False,
                        "is_section_header": True,
                    }
                    i += 1
                    continue

                # Look for test name underlined (common pytest pattern for test start)
                elif (
                    in_failures_section
                    and line.startswith("_")
                    and i + 1 < len(all_lines)
                    and not all_lines[i + 1].strip().startswith("_")
                ):
                    # This is a test name header
                    if current_block["lines"]:
                        test_blocks.append(current_block)

                    # Get the test name from the next line
                    test_name_line = (
                        all_lines[i + 1].strip() if i + 1 < len(all_lines) else ""
                    )

                    # Create new test block
                    current_block = {
                        "lines": [all_lines[i], test_name_line],
                        "start_line": i,
                        "is_test": True,
                        "test_name": test_name_line,
                    }
                    i += 2  # Skip the test name line
                    continue

                # Detect log capture section within a test
                elif any(marker in line for marker in log_markers):
                    # Keep in the same block but mark the line for special processing
                    current_block["lines"].append("### LOG CAPTURE START ###")
                    current_block["lines"].append(all_lines[i])
                    i += 1
                    continue

                # Detect "short test summary info" section
                elif line.startswith("=") and "short test summary info" in line:
                    in_failures_section = False
                    if current_block["lines"]:
                        test_blocks.append(current_block)

                    current_block = {
                        "lines": [all_lines[i]],
                        "start_line": i,
                        "is_test": False,
                        "is_summary": True,
                    }
                    i += 1
                    continue

                # Default: add to current block
                else:
                    current_block["lines"].append(all_lines[i])
                    i += 1

            # Add the last block
            if current_block["lines"]:
                test_blocks.append(current_block)

            # Second pass: process blocks into proper test records
            for block_idx, block in enumerate(test_blocks):
                if block.get("is_test", False):
                    # Process a test failure block
                    content = "\n".join(block["lines"])

                    # Extract file path and line number
                    file_path = "Unknown"
                    line_number = "?"
                    test_name = block.get("test_name", "Unknown Test")

                    # Find the first line with a file path
                    for line in block["lines"]:
                        if "tests/" in line and ".py:" in line:
                            parts = line.split(".py:")
                            if len(parts) > 1:
                                file_path = parts[0] + ".py"
                                line_parts = parts[1].split(":", 1)
                                if line_parts and line_parts[0].isdigit():
                                    line_number = line_parts[0]
                                break

                    # Extract the test function name
                    if "test_" in test_name:
                        test_func = (
                            test_name.split("test_")[1].split()[0]
                            if "test_" in test_name
                            else "unknown"
                        )
                        test_name = "test_" + test_func

                    # Extract primary error and secondary errors
                    primary_error = ""
                    secondary_error = ""
                    captured_logs = ""

                    in_primary = False
                    in_secondary = False
                    in_logs = False

                    primary_lines = []
                    secondary_lines = []
                    log_lines = []

                    for line in block["lines"]:
                        if "E   " in line:
                            # This is an error line
                            if "During handling of the above exception" in line:
                                in_primary = False
                                in_secondary = True
                                continue

                            if in_secondary:
                                secondary_lines.append(line)
                            else:
                                in_primary = True
                                primary_lines.append(line)

                        elif "### LOG CAPTURE START ###" in line:
                            in_logs = True
                            in_primary = False
                            in_secondary = False
                            continue

                        elif in_logs:
                            log_lines.append(line)

                        elif in_primary:
                            primary_lines.append(line)

                        elif in_secondary:
                            secondary_lines.append(line)

                    # Format the errors and logs
                    if primary_lines:
                        primary_error = "\n".join(primary_lines)

                    if secondary_lines:
                        secondary_error = (
                            "During handling of the above exception, another exception occurred:\n"
                            + "\n".join(secondary_lines)
                        )

                    if log_lines:
                        captured_logs = "\n".join(log_lines)

                    # Create the test info record with enhanced error information
                    test_info = {
                        "file": file_path,
                        "line": line_number,
                        "name": test_name,
                        "status": "failed",
                        "primary_error": primary_error,
                        "secondary_error": secondary_error,
                        "logs": captured_logs,
                        "summary": f"Test failed with {primary_error.splitlines()[0] if primary_lines else 'an unknown error'}",
                        "output": content,
                    }
                    tests.append(test_info)

                elif block.get("is_section_header", False) or block.get(
                    "is_summary", False
                ):
                    # These are section headers, we can keep them as context
                    content = "\n".join(block["lines"])
                    section_name = (
                        "Test Summary"
                        if block.get("is_summary", False)
                        else "Failures Section"
                    )

                    test_info = {
                        "file": "Test Report",
                        "name": section_name,
                        "status": "info",
                        "summary": section_name,
                        "output": content,
                    }
                    tests.append(test_info)
                elif block_idx == 0:
                    # This is likely the test setup/configuration block
                    content = "\n".join(block["lines"])
                    test_info = {
                        "file": "Test Setup",
                        "name": "Configuration",
                        "status": "info",
                        "summary": "Test configuration and setup",
                        "output": content,
                    }
                    tests.append(test_info)
                else:
                    # Other miscellaneous blocks
                    content = "\n".join(block["lines"])
                    test_info = {
                        "file": "Other",
                        "name": f"Block {block_idx}",
                        "status": "info",
                        "summary": "Additional test information",
                        "output": content,
                    }
                    tests.append(test_info)

            # Update the test template to better display database connection errors
            test_template = """
            <div class="test-details test-{status}" data-status="{status}">
                <div class="card-header collapsible">
                    <span>
                        <span class="icon">
                            <i class="fas {icon_class}"></i>
                        </span>
                        {file}:{line} :: {name}
                    </span>
                    <span class="status-badge {status}">{status_text}</span>
                </div>
                <div class="content">
                    <div class="test-summary"><strong>Summary:</strong> {summary}</div>

                    {primary_error_section}
                    {secondary_error_section}
                    {logs_section}

                    <div class="test-output-header">Full Test Output:</div>
                    <div class="test-output">{output}</div>
                </div>
            </div>
            """

            # Update the CSS to better handle the error display
            additional_css = """
            .test-output-header {
                font-weight: bold;
                margin-top: 10px;
                padding: 5px;
                background-color: var(--bg-light);
                border-top: 1px solid var(--border-color);
            }
            .error-section {
                background-color: var(--error-light);
                padding: 10px;
                margin: 5px 0;
                border-radius: 4px;
                border-left: 3px solid var(--error-color);
                white-space: pre-wrap;
                font-family: monospace;
            }
            .logs-section {
                background-color: var(--info-light);
                padding: 10px;
                margin: 5px 0;
                border-radius: 4px;
                border-left: 3px solid var(--info-color);
                white-space: pre-wrap;
                font-family: monospace;
            }
            """

            # Generate the test results HTML with our enhanced template
            test_results_html = ""
            for test in tests:
                # Set up icon based on status
                if test["status"] == "passed":
                    icon_class = "fa-check text-passed"
                    status_text = "Passed"
                elif test["status"] == "failed":
                    icon_class = "fa-times text-failed"
                    status_text = "Failed"
                elif test["status"] == "skipped":
                    icon_class = "fa-forward text-skipped"
                    status_text = "Skipped"
                else:
                    icon_class = "fa-info-circle"
                    status_text = "Info"

                # Create the error sections
                primary_error_section = ""
                if test.get("primary_error"):
                    primary_error_section = f"""
                    <div class="error-section">
                        <strong>Primary Error:</strong>
                        <div>{test["primary_error"]}</div>
                    </div>
                    """

                secondary_error_section = ""
                if test.get("secondary_error"):
                    secondary_error_section = f"""
                    <div class="error-section">
                        <strong>Secondary Error:</strong>
                        <div>{test["secondary_error"]}</div>
                    </div>
                    """

                logs_section = ""
                if test.get("logs"):
                    logs_section = f"""
                    <div class="logs-section">
                        <strong>Captured Logs:</strong>
                        <div>{test["logs"]}</div>
                    </div>
                    """

                # Fill in template
                line = test.get("line", "")
                test_html = test_template.format(
                    status=test["status"],
                    icon_class=icon_class,
                    file=test["file"],
                    line=line,
                    name=test["name"],
                    status_text=status_text,
                    summary=test.get("summary", "Test result"),
                    primary_error_section=primary_error_section,
                    secondary_error_section=secondary_error_section,
                    logs_section=logs_section,
                    output=test["output"],
                )
                test_results_html += test_html

            # Create a simple HTML report with better formatting and interactive features
            with open(report_path, 'w', encoding='utf-8') as f:
                # First part of the HTML with dynamic content
                f.write(
                    f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Test Report - {cli_args.category or 'All'} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        :root {{
            --primary-color: #2563eb;
            --primary-light: #dbeafe;
            --success-color: #16a34a;
            --success-light: #dcfce7;
            --error-color: #dc2626;
            --error-light: #fee2e2;
            --warning-color: #d97706;
            --warning-light: #fef3c7;
            --info-color: #0891b2;
            --info-light: #e0f2fe;
            --text-color: #1f2937;
            --text-light: #6b7280;
            --bg-color: #ffffff;
            --bg-light: #f9fafb;
            --border-color: #e5e7eb;
            --header-bg: #1e293b;  /* Dark background for header instead of blue */
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: var(--text-color);
            background-color: var(--bg-light);
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background-color: var(--header-bg);
            color: white;
            padding: 1rem;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header-container {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .logo {{
            height: 40px;
            width: auto;
            object-fit: contain;
        }}
        .card {{
            background-color: var(--bg-color);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            overflow: hidden;
        }}
        .card-header {{
            background-color: var(--bg-light);
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card-header h2, .card-header h3 {{
            margin: 0;
            font-size: 1.2rem;
        }}
        .card-body {{
            padding: 1rem;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .summary-item {{
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-passed {{
            background-color: var(--success-light);
            color: var (--success-color);
        }}
        .summary-failed {{
            background-color: var(--error-light);
            color: var(--error-color);
        }}
        .summary-skipped {{
            background-color: var(--warning-light);
            color: var(--warning-color);
        }}
        .summary-all {{
            background-color: var(--info-light);
            color: var(--info-color);
        }}
        .summary-number {{
            font-size: 2rem;
            font-weight: bold;
            display: block;
            margin-bottom: 0.5rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
        }}
        th, td {{
            padding: 0.75rem;
            border-bottom: 1px solid var(--border-color);
            text-align: left;
        }}
        th {{
            background-color: var(--bg-light);
            font-weight: 600;
        }}
        tr:hover {{
            background-color: var(--bg-light);
        }}
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: 500;
        }}
        .passed {{
            background-color: var(--success-light);
            color: var (--success-color);
        }}
        .failed {{
            background-color: var(--error-light);
            color: var(--error-color);
        }}
        .skipped {{
            background-color: var(--warning-light);
            color: var(--warning-color);
        }}
        .unknown {{
            background-color: var(--info-light);
            color: var(--info-color);
        }}
        .text-passed {{
            color: var(--success-color);
        }}
        .text-failed {{
            color: var(--error-color);
        }}
        .text-skipped {{
            color: var(--warning-color);
        }}
        .collapsible {{
            cursor: pointer;
        }}
        .collapsible:after {{
            content: "\\f078";
            font-family: "Font Awesome 5 Free";
            font-weight: 900;
            float: right;
            margin-left: 5px;
        }}
        .active:after {{
            content: "\\f077";
            font-family: "Font Awesome 5 Free";
            font-weight: 900;
        }}
        .content {{
            display: none;
            overflow: hidden;
            padding: 0;
            background-color: white;
        }}
        .test-details {{
            border-left: 4px solid var(--border-color);
            margin: 1rem 0;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .test-passed {{
            border-left-color: var(--success-color);
        }}
        .test-failed {{
            border-left-color: var(--error-color);
        }}
        .test-skipped {{
            border-left-color: var(--warning-color);
        }}
        .test-summary {{
            background-color: var(--bg-color);
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            font-size: 1rem;
        }}
        .test-reason {{
            background-color: var(--bg-color);
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        .reason-content {{
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            padding: 0.5rem;
            background-color: var(--bg-light);
            border-radius: 4px;
        }}
        .test-output {{
            background-color: var(--bg-light);
            padding: 1rem;
            border-radius: 0 0 4px 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.9rem;
            margin: 0;
            border-top: 1px solid var(--border-color);
        }}
        .filter-controls {{
            margin-bottom: 1rem;
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            border: none;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }}
        .filter-btn:hover {{
            background-color: var(--bg-light);
        }}
        .filter-btn.active {{
            background-color: var(--primary-light);
            border-color: var(--primary-color);
            color: var(--primary-color);
        }}
        .icon {{
            display: inline-block;
            width: 20px;
            text-align: center;
        }}
        pre {{
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            margin: 0;
            padding: 1rem;
            background-color: var(--bg-light);
            border-radius: 4px;
            overflow-x: auto;
        }}
        button.collapsible {{
            background-color: var(--bg-light);
            padding: 0.75rem 1rem;
            width: 100%;
            border: 1px solid var(--border-color);
            text-align: left;
            outline: none;
            border-radius: 4px;
            margin-bottom: 0.5rem;
            transition: background-color 0.2s;
            font-weight: 500;
        }}
        button.collapsible:hover {{
            background-color: #e5e7eb;
        }}
        {additional_css}
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-container">
                <img class="logo" src="data:image/svg+xml;base64,{encode_logo_as_base64()}" alt="Logo">
                <h1>Test Report - {cli_args.category or 'All'}</h1>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="card">
            <div class="card-header">
                <h2>Test Summary</h2>
                <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="card-body">
                <div class="summary">
                    <div class="summary-item summary-all">
                        <span class="summary-number">{len([t for t in tests if t.get('is_test', True) and t['status'] != 'info'])}</span>
                        <span>Total Tests</span>
                    </div>
                    <div class="summary-item summary-passed">
                        <span class="summary-number">{sum(1 for t in tests if t['status'] == 'passed')}</span>
                        <span>Passed</span>
                    </div>
                    <div class="summary-item summary-failed">
                        <span class="summary-number">{sum(1 for t in tests if t['status'] == 'failed')}</span>
                        <span>Failed</span>
                    </div>
                    <div class="summary-item summary-skipped">
                        <span class="summary-number">{sum(1 for t in tests if t['status'] == 'skipped')}</span>
                        <span>Skipped</span>
                    </div>
                </div>

                <table>
                    <tr>
                        <th>Category</th>
                        <td>{cli_args.category or 'All'}</td>
                    </tr>
                    <tr>
                        <th>Marker</th>
                        <td>{cli_args.marker or 'None'}</td>
                    </tr>
                    <tr>
                        <th>Keyword</th>
                        <td>{cli_args.keyword or 'None'}</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td><span class="status-badge {test_status.lower()}">{test_status}</span></td>
                    </tr>
                    <tr>
                        <th>Return Code</th>
                        <td>{result.returncode}</td>
                    </tr>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2>Test Results</h2>
            </div>
            <div class="card-body">
                <div class="filter-controls">
                    <button class="filter-btn active" data-filter="all">
                        <span class="icon"><i class="fas fa-list"></i></span>
                        All Tests
                    </button>
                    <button class="filter-btn" data-filter="passed">
                        <span class="icon"><i class="fas fa-check text-passed"></i></span>
                        Passed
                    </button>
                    <button class="filter-btn" data-filter="failed">
                        <span class="icon"><i class="fas fa-times text-failed"></i></span>
                        Failed
                    </button>
                    <button class="filter-btn" data-filter="skipped">
                        <span class="icon"><i class="fas fa-forward text-skipped"></i></span>
                        Skipped
                    </button>
                </div>

                <div id="test-results">
                    {test_results_html}
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2>Raw Test Output</h2>
            </div>
            <div class="card-body">
                <button class="collapsible">Show Raw Test Output</button>
                <div class="content">
                    <pre>{result.stdout}</pre>
                </div>

                <button class="collapsible">Show Error Output</button>
                <div class="content">
                    <pre>{result.stderr if result.stderr else "No errors reported."}</pre>
                </div>
            </div>
        </div>
    </div>"""
                )

                # JavaScript part as a regular string, NOT an f-string
                f.write("""
    <script>
        // Initialize all collapsible elements
        document.addEventListener('DOMContentLoaded', function() {
            // Collapsible sections
            var coll = document.getElementsByClassName("collapsible");
            for (var i = 0; i < coll.length; i++) {
                coll[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.display === "block") {
                        content.style.display = "none";
                    } else {
                        content.style.display = "block";
                    }
                });
            }

            // Filter functionality
            var filterBtns = document.querySelectorAll('.filter-btn');
            filterBtns.forEach(function(btn) {
                btn.addEventListener('click', function() {
                    // Remove active class from all buttons
                    filterBtns.forEach(function(innerBtn) {
                        innerBtn.classList.remove('active');
                    });

                    // Add active class to clicked button
                    this.classList.add('active');

                    // Get filter value
                    var filter = this.getAttribute('data-filter');

                    // Filter test results
                    var testResults = document.querySelectorAll('#test-results .test-details');
                    testResults.forEach(function(test) {
                        if (filter === 'all' || test.getAttribute('data-status') === filter) {
                            test.style.display = 'block';
                        } else {
                            test.style.display = 'none';
                        }
                    });
                });
            });

            // Auto-open failed tests
            var failedTests = document.querySelectorAll('.test-failed .collapsible');
            failedTests.forEach(function(test) {
                test.click();
            });
        });
    </script>
</body>
</html>
""")

            # Print test output
            print(result.stdout)
            if result.stderr:
                print("Errors:", file=sys.stderr)
                print(result.stderr, file=sys.stderr)

            # Check if tests were run
            tests_were_run = not "no tests ran" in result.stdout.lower()

            if tests_were_run:

                # Create a summary file
                summary_path = report_dir / "summary.txt"
                with open(summary_path, "w") as f:
                    f.write(f"Test Run Summary\n")
                    f.write(f"=======================================\n")
                    f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Category: {cli_args.category or 'All'}\n")
                    f.write(f"Marker: {cli_args.marker or 'None'}\n")
                    f.write(f"Keyword: {cli_args.keyword or 'None'}\n")
                    f.write(f"Status: {'Failed' if result.returncode else 'Passed'}\n")

                    # Extract test counts from output
                    for line in result.stdout.splitlines():
                        if line.strip().startswith("collected ") and "item" in line:
                            f.write(f"Tests: {line.strip()}\n")
                            break
                    f.write(f"=======================================\n")

                print(f"\n{'❌ Some tests failed.' if result.returncode else '✅ All tests passed.'}")
                print(f"Check the HTML report at {report_path} for details")

                # Print basic test summary
                duration = "unknown"
                for line in result.stdout.splitlines():
                    if " in " in line and line.strip().endswith("s"):
                        duration = line.split("in ")[-1].strip()
                        break

                print("\nTest Summary:")
                print(f"  - Duration: {duration}")
                print(f"  - Category: {cli_args.category or 'All'}")
                print(f"  - Marker: {cli_args.marker or 'None'}")

                # Open the report in browser if requested and not explicitly disabled
                should_open_browser = cli_args.browser or (not cli_args.no_browser and not args)
                if should_open_browser and report_path.exists():
                    try:
                        webbrowser.open(f"file://{report_path.absolute()}")
                        print(f"Opening report in browser: {report_path.absolute()}")
                    except Exception as e:
                        print(f"Could not open browser: {e}")
            else:
                print("\n❌ No tests were run or collected. Check the output for errors.")
                print("No report file was generated as there were no test results.")

            return result.returncode

    except Exception as e:
        print(f"\n❌ Error running tests: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        # Ensure virtual environment is active
        ensure_venv()

        # Ensure dependencies
        ensure_dependencies()

        # Run tests with parsed arguments directly
        sys.exit(run_tests())
    except KeyboardInterrupt:
        print("\n\n❌ Test run cancelled by user")
        sys.exit(1)
