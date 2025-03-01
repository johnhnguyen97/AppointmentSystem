import json
import os
import subprocess
import getpass
from typing import Dict, Any, Optional

def get_bitwarden_credentials(item_name: str, field_names: Optional[list] = None) -> Dict[str, Any]:
    """
    Retrieve credentials from Bitwarden vault
    
    Args:
        item_name: Name of the item in Bitwarden vault
        field_names: List of field names to extract (if None, extracts all fields)
        
    Returns:
        Dictionary containing the requested credentials
    """
    try:
        # Get API key credentials from environment variables
        client_id = os.environ.get("BW_CLIENTID")
        client_secret = os.environ.get("BW_CLIENTSECRET")
        
        if not client_id or not client_secret:
            raise ValueError("Bitwarden API credentials not found in environment variables")
        
        # Set environment variables for Bitwarden API
        env = os.environ.copy()
        env["BW_CLIENTID"] = client_id
        env["BW_CLIENTSECRET"] = client_secret
        
        # Check if already logged in
        status_result = subprocess.run(
            ['bw', 'status'],
            capture_output=True,
            text=True,
            env=env
        )
        
        status = json.loads(status_result.stdout)
        session_key = None
        
        # Check login status
        if status.get('status') == 'unlocked':
            # Already logged in and unlocked
            print("Using existing unlocked Bitwarden session")
            session_key = os.environ.get("BW_SESSION")
            if not session_key:
                # Get session key by prompting for master password
                print("Bitwarden vault is unlocked but session key not found in environment")
                master_password = getpass.getpass("Enter your Bitwarden master password: ")
                unlock_result = subprocess.run(
                    ['bw', 'unlock', master_password, '--raw'],
                    capture_output=True,
                    text=True,
                    env=env
                )
                if unlock_result.returncode == 0:
                    session_key = unlock_result.stdout.strip()
                else:
                    raise RuntimeError(f"Failed to unlock Bitwarden: {unlock_result.stderr}")
        elif status.get('status') == 'locked':
            # Logged in but locked
            print("Bitwarden vault is locked")
            master_password = getpass.getpass("Enter your Bitwarden master password: ")
            unlock_result = subprocess.run(
                ['bw', 'unlock', master_password, '--raw'],
                capture_output=True,
                text=True,
                env=env
            )
            if unlock_result.returncode == 0:
                session_key = unlock_result.stdout.strip()
            else:
                raise RuntimeError(f"Failed to unlock Bitwarden: {unlock_result.stderr}")
        else:
            # Not logged in
            print("Logging in to Bitwarden with API key")
            try:
                login_result = subprocess.run(
                    ['bw', 'login', '--apikey', '--raw'],
                    capture_output=True,
                    text=True,
                    env=env
                )
                if login_result.returncode == 0:
                    session_key = login_result.stdout.strip()
                else:
                    # If login fails because already logged in, try to unlock
                    if "already logged in" in login_result.stderr:
                        print("Already logged in to Bitwarden")
                        master_password = getpass.getpass("Enter your Bitwarden master password: ")
                        unlock_result = subprocess.run(
                            ['bw', 'unlock', master_password, '--raw'],
                            capture_output=True,
                            text=True,
                            env=env
                        )
                        if unlock_result.returncode == 0:
                            session_key = unlock_result.stdout.strip()
                        else:
                            raise RuntimeError(f"Failed to unlock Bitwarden: {unlock_result.stderr}")
                    else:
                        raise RuntimeError(f"Failed to login to Bitwarden: {login_result.stderr}")
            except Exception as e:
                raise RuntimeError(f"Error during Bitwarden login: {str(e)}")
        
        if not session_key:
            raise RuntimeError("Failed to get Bitwarden session key")
        
        # Get the requested item
        result = subprocess.run(
            ['bw', 'get', 'item', item_name, '--session', session_key],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        
        # Parse the JSON output
        item = json.loads(result.stdout)
        
        # Extract credentials
        credentials = {}
        
        # Get username and password from login data
        login_data = item.get('login', {})
        if 'username' in login_data:
            credentials['username'] = login_data.get('username')
        if 'password' in login_data:
            credentials['password'] = login_data.get('password')
        
        # Get custom fields
        for field in item.get('fields', []):
            field_name = field.get('name')
            if field_names is None or field_name in field_names:
                credentials[field_name] = field.get('value')
        
        # Get notes if needed (often contains JSON or other structured data)
        notes = item.get('notes')
        if notes:
            try:
                # Try to parse notes as JSON
                notes_data = json.loads(notes)
                for key, value in notes_data.items():
                    if field_names is None or key in field_names:
                        credentials[key] = value
            except json.JSONDecodeError:
                # If not JSON, store as raw notes
                if field_names is None or 'notes' in field_names:
                    credentials['notes'] = notes
        
        return credentials
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Bitwarden CLI error: {e.stderr}"
        raise RuntimeError(error_msg) from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Bitwarden output as JSON: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"Error retrieving credentials from Bitwarden: {str(e)}") from e

def get_service_config(service_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific service from Bitwarden
    
    Args:
        service_name: Name of the service (used as item name in Bitwarden)
        
    Returns:
        Dictionary with service configuration
    """
    return get_bitwarden_credentials(f"{service_name} Configuration")

def get_database_credentials() -> Dict[str, str]:
    """
    Get database credentials for the Nail Appointment Database
    
    Returns:
        Dictionary with database connection parameters
    """
    # Use the correct database connection details directly
    creds = {
        'host': 'nail-appointment-db-appointmentsystem.e.aivencloud.com',
        'port': '23309',
        'database': 'defaultdb',
        'username': 'avnadmin',
        'password': 'AVNS_IouBYATtqgwj42TCq5l'
    }
    
    print(f"Database connection details: host={creds['host']}, port={creds['port']}, database={creds['database']}")
    
    return creds
