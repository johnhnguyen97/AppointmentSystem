import os
import subprocess
from dotenv import load_dotenv

def test_bws_access():
    # Load environment variables from .env
    load_dotenv()

    # Get access token
    access_token = os.environ.get("BWS_ACCESS_TOKEN")
    if not access_token:
        print("BWS_ACCESS_TOKEN not found in .env file")
        return

    # Print token (masked) for debugging
    masked_token = access_token[:10] + "..." + access_token[-10:]
    print(f"Using access token: {masked_token}")

    # Try direct command execution
    cmd = ['.\\tools\\bws.exe', 'secret', 'get', '8fc2205d-8981-45d4-9f64-b29a00047d75', '--access-token', access_token]
    print(f"Executing command: bws.exe secret get <secret-id> --access-token <token>")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout[:100]}...")
        if result.stderr:
            print(f"Error: {result.stderr}")

    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_bws_access()
