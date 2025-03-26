#!/usr/bin/env python3
"""
Generate a direct test report without relying on pytest-html
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import re

# Directory setup
REPO_ROOT = Path(__file__).parent.parent
REPORT_DIR = REPO_ROOT / "test-reports"
REPORT_DIR.mkdir(exist_ok=True)
REPORT_PATH = REPORT_DIR / "manual-report.html"

def run_pytest():
    """Run pytest and capture the output in JSON format"""
    cmd = [
        sys.executable, "-m", "pytest",
        "--json-report", "--json-report-file=test-results.json",
        "-v"
    ]

    # Add any arguments from command line
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])

    print(f"Running tests: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=REPO_ROOT)

    # Check if the JSON report exists
    json_path = REPO_ROOT / "test-results.json"
    if not json_path.exists():
        # Fallback to capturing text output
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        return None, result.stdout, result.stderr

    # Load the JSON report
    with open(json_path) as f:
        data = json.load(f)

    # Remove the temporary JSON file
    json_path.unlink()

    return data, "", ""

def extract_test_results(stdout):
    """Extract test results from stdout if JSON report is not available"""
    passed = []
    failed = []
    skipped = []

    # Regular expressions to extract test results
    pass_pattern = r"PASSED\s+(.*?)\s+\[\s*\d+%\]"
    fail_pattern = r"FAILED\s+(.*?)\s+\[\s*\d+%\]"
    skip_pattern = r"SKIPPED\s+(.*?)\s+\[\s*\d+%\]"

    for line in stdout.splitlines():
        if "PASSED" in line:
            match = re.search(pass_pattern, line)
            if match:
                passed.append(match.group(1).strip())
        elif "FAILED" in line:
            match = re.search(fail_pattern, line)
            if match:
                failed.append(match.group(1).strip())
        elif "SKIPPED" in line:
            match = re.search(skip_pattern, line)
            if match:
                skipped.append(match.group(1).strip())

    return passed, failed, skipped

def generate_html_report(json_data, stdout, stderr):
    """Generate an HTML report from the test results"""
    if json_data:
        # Process JSON data
        passed = [test["nodeid"] for test in json_data.get("tests", []) if test.get("outcome") == "passed"]
        failed = [test["nodeid"] for test in json_data.get("tests", []) if test.get("outcome") == "failed"]
        skipped = [test["nodeid"] for test in json_data.get("tests", []) if test.get("outcome") == "skipped"]
        summary = json_data.get("summary", {})
    else:
        # Process stdout
        passed, failed, skipped = extract_test_results(stdout)
        summary = {
            "passed": len(passed),
            "failed": len(failed),
            "skipped": len(skipped),
            "total": len(passed) + len(failed) + len(skipped)
        }

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-bottom: 1px solid #ddd; }}
        .summary {{ display: flex; margin: 20px 0; }}
        .summary-item {{ margin-right: 20px; padding: 10px; border-radius: 4px; }}
        .passed {{ background-color: rgba(0, 128, 0, 0.1); color: green; }}
        .failed {{ background-color: rgba(255, 0, 0, 0.1); color: red; }}
        .skipped {{ background-color: rgba(255, 165, 0, 0.1); color: orange; }}
        .test-item {{ margin-bottom: 5px; padding: 8px; border-radius: 4px; }}
        h2 {{ margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        pre {{ background-color: #f8f8f8; border: 1px solid #ddd; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <div class="summary-item passed">
            <h3>Passed: {summary.get("passed", len(passed))}</h3>
        </div>
        <div class="summary-item failed">
            <h3>Failed: {summary.get("failed", len(failed))}</h3>
        </div>
        <div class="summary-item skipped">
            <h3>Skipped: {summary.get("skipped", len(skipped))}</h3>
        </div>
        <div class="summary-item">
            <h3>Total: {summary.get("total", len(passed) + len(failed) + len(skipped))}</h3>
        </div>
    </div>

    <h2>Passed Tests</h2>
    {"".join([f'<div class="test-item passed">{test}</div>' for test in passed]) if passed else "<p>No passed tests</p>"}

    <h2>Failed Tests</h2>
    {"".join([f'<div class="test-item failed">{test}</div>' for test in failed]) if failed else "<p>No failed tests</p>"}

    <h2>Skipped Tests</h2>
    {"".join([f'<div class="test-item skipped">{test}</div>' for test in skipped]) if skipped else "<p>No skipped tests</p>"}

    <h2>Console Output</h2>
    <pre>{stdout}</pre>

    <h2>Error Output</h2>
    <pre>{stderr}</pre>
</body>
</html>
"""

    # Write the HTML report
    with open(REPORT_PATH, 'w') as f:
        f.write(html)

    print(f"Report generated at: {REPORT_PATH}")

if __name__ == "__main__":
    # Check if pytest-json-report is installed, install if needed
    try:
        import pytest_jsonreport
    except ImportError:
        print("Installing pytest-json-report...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest-json-report"])

    json_data, stdout, stderr = run_pytest()
    generate_html_report(json_data, stdout, stderr)
    print("✅ Report generation complete")
