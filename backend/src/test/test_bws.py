import os
from dotenv import load_dotenv
import subprocess
import pytest

def test_bws_connection():
    """Test Bitwarden Secrets Manager connection"""
    # Load environment variables from .env
    load_dotenv()
    # Explicitly set PROJECT_ID
    os.environ['PROJECT_ID'] = '154198ca-462d-4059-87e2-b29a0002f50b'

    try:
        # Use the PROJECT_ID from .env to list secrets
        result = subprocess.run(
            ['tools/bws.exe', 'secret', 'list', os.getenv('PROJECT_ID')],  # Note the commas between arguments
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ}  # Pass all environment variables including BWS_ACCESS_TOKEN
        )

        print("Bitwarden Secrets Output:", result.stdout)
        assert result.returncode == 0, "bws command failed"

    except subprocess.CalledProcessError as e:
        pytest.fail(f"bws command failed: {e.stderr}")
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
