#!/usr/bin/env python3
"""
Script to run tests and generate proper HTML reports
"""
import os
import sys
import subprocess
import logging
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def ensure_dependencies():
    """Ensure all required dependencies are installed"""
    required_packages = ['pytest', 'pytest-html']
    missing_packages = []

    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)

    if missing_packages:
        logger.warning(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Installing missing packages...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
        logger.info("✅ Packages installed successfully")
    else:
        logger.info("✅ All required dependencies are installed")

def run_tests():
    """Run pytest with proper configuration"""
    # Make sure dependencies are installed
    ensure_dependencies()

    # Ensure the report directory exists with proper permissions
    report_dir = Path(__file__).parent.parent / "test-reports"
    report_dir.mkdir(exist_ok=True, mode=0o755)

    # Create an empty CSS file to ensure the directory is writable
    css_test_file = report_dir / "test.css"
    css_test_file.write_text("/* Test write permissions */")
    css_test_file.unlink(missing_ok=True)

    logger.info(f"Report directory ready: {report_dir}")

    # Build the pytest command with explicit HTML report parameters
    report_path = str(report_dir / "report.html")
    cmd = [
        sys.executable, "-m", "pytest",
        f"--html={report_path}",
        "--self-contained-html",
    ]

    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])

    logger.info(f"Running tests with command: {' '.join(cmd)}")

    try:
        # Run the tests with environment variables set
        env = os.environ.copy()
        env["PYTEST_ADDOPTS"] = f"--html={report_path} --self-contained-html"

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            env=env,
            capture_output=True,
            text=True
        )

        # Log output for debugging
        logger.info("Test output:")
        logger.info(result.stdout)

        if result.stderr:
            logger.warning("Test errors:")
            logger.warning(result.stderr)

        # Check if HTML report was generated
        if Path(report_path).exists() and Path(report_path).stat().st_size > 0:
            logger.info(f"✅ HTML report generated successfully at: {report_path}")
        else:
            logger.error("❌ HTML report was not generated or is empty")
            # Manually create a basic HTML report if automated one failed
            create_manual_report(report_path, result.stdout, result.stderr)

        return result.returncode == 0
    except Exception as e:
        logger.error(f"❌ Error running tests: {str(e)}")
        return False

def create_manual_report(path, stdout, stderr):
    """Create a manual HTML report when automatic generation fails"""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        pre {{ background-color: #f5f5f5; padding: 10px; overflow: auto; }}
    </style>
</head>
<body>
    <h1>Test Report (Manual Generation)</h1>
    <p class="error">The automatic HTML report generation failed. This is a manually generated fallback report.</p>

    <h2>Test Output</h2>
    <pre>{stdout}</pre>

    <h2>Error Output</h2>
    <pre class="error">{stderr}</pre>
</body>
</html>
"""
    try:
        with open(path, 'w') as f:
            f.write(html_content)
        logger.info(f"✅ Manual HTML report generated at: {path}")
    except Exception as e:
        logger.error(f"❌ Failed to create manual report: {str(e)}")

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
