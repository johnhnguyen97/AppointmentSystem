#!/usr/bin/env python3
"""
Script to apply database permissions using environment variables
"""
import os
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get database connection details from environment variables
DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
DB_PORT = os.getenv("TEST_DB_PORT", "5432")
DB_NAME = os.getenv("TEST_DB_NAME", "appointmentsystem_test")
DB_USER = os.getenv("ADMIN_DB_USER", "postgres")
DB_PASSWORD = os.getenv("ADMIN_DB_PASSWORD", "")
TEST_USER = os.getenv("TEST_DB_USER", "test_admin")

def run_permission_script():
    """Run the SQL permission script with environment variables"""
    script_path = Path(__file__).parent / "grant_test_permissions.sql"

    if not script_path.exists():
        logger.error(f"Permission script not found: {script_path}")
        return False

    # Build the psql command
    cmd = [
        "psql",
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "-f", str(script_path),
        "-v", f"test_db_user={TEST_USER}",
        "-v", f"test_db={DB_NAME}"
    ]

    try:
        logger.info(f"Running permission script with user: {TEST_USER}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Permission script executed successfully")
        logger.debug(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing permission script: {e}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return False

if __name__ == "__main__":
    if run_permission_script():
        logger.info("✅ Database permissions applied successfully")
    else:
        logger.error("❌ Failed to apply database permissions")
