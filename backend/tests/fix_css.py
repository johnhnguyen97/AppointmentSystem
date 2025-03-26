"""Utility to fix CSS file issues with pytest-html."""
import os
import sys
from pathlib import Path
import shutil
import subprocess

def ensure_setuptools():
    """Ensure setuptools is installed for pkg_resources."""
    try:
        import pkg_resources
        print("pkg_resources is available")
    except ImportError:
        print("Installing setuptools (provides pkg_resources)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "setuptools"], check=True)
        print("Setuptools installed successfully")

def check_pytest_html_version():
    """Check the installed version of pytest-html."""
    # First ensure setuptools is available
    ensure_setuptools()

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pytest-html"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Installed pytest-html:")
        print(result.stdout)

        # Check for known problematic versions
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                version = line.split(":", 1)[1].strip()
                print(f"Detected version: {version}")

                # Add version-specific advice
                if version.startswith("3."):
                    print("Note: pytest-html 3.x has different CSS handling than 2.x")
                    print("Consider downgrading to 2.1.1 if problems persist")
    except Exception as e:
        print(f"Error checking pytest-html version: {e}")
        print("Attempting to reinstall pytest-html...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "pytest-html==2.1.1"], check=False)

def fix_css_file():
    """Fix the CSS file by creating a minimal working version."""
    css_path = Path("tests/assets/custom_style.css")
    backup_path = css_path.with_suffix(".css.bak")

    # Backup existing file if it exists
    if css_path.exists():
        print(f"Backing up existing CSS file to {backup_path}")
        shutil.copy2(css_path, backup_path)

    # Create minimal CSS file that should work with pytest-html
    print(f"Creating minimal CSS file at {css_path}")
    with open(css_path, "w") as f:
        f.write("""
/* Minimal pytest-html styling */
body {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 12px;
  min-width: 800px;
  color: #999;
}
h1 {
  font-size: 24px;
  color: black;
}
h2 {
  font-size: 16px;
  color: black;
}
p {
  color: black;
}
a {
  color: #999;
}
table {
  border-collapse: collapse;
}
.passed {
  color: green;
}
.failed, .error {
  color: red;
}
.skipped {
  color: orange;
}
""")

    # Verify the file
    if css_path.exists():
        size = css_path.stat().st_size
        print(f"CSS file created successfully ({size} bytes)")

        # Check file permissions
        print("Checking file permissions...")
        try:
            with open(css_path, "r") as f:
                content = f.read()
            print(f"File is readable, contains {len(content)} characters")
        except Exception as e:
            print(f"Error reading file: {e}")

def test_css_parsing():
    """Test if the CSS file can be parsed without errors."""
    css_path = Path("tests/assets/custom_style.css")
    if not css_path.exists():
        print(f"CSS file not found at {css_path}")
        return

    try:
        with open(css_path, "r") as f:
            css_content = f.read()

        # Check for common syntax errors
        if "{" in css_content and "}" not in css_content:
            print("Warning: Unbalanced curly braces in CSS file")

        if "/*" in css_content and "*/" not in css_content:
            print("Warning: Unclosed comment in CSS file")

        # Check for non-ASCII characters
        has_non_ascii = any(not c.isascii() for c in css_content)
        if has_non_ascii:
            print("Warning: CSS file contains non-ASCII characters that might cause issues")

        print("Basic CSS syntax check passed")
    except Exception as e:
        print(f"Error analyzing CSS file: {e}")

if __name__ == "__main__":
    print("CSS file troubleshooter for pytest-html")
    print("=====================================")

    # Ensure setuptools
    ensure_setuptools()

    # Check pytest-html version
    check_pytest_html_version()

    # Fix the CSS file
    fix_css_file()

    # Test CSS parsing
    test_css_parsing()

    print("\nDone! Try running your tests again with the fixed CSS file.")
    print("If problems persist, run tests without custom CSS by removing the --css option.")
