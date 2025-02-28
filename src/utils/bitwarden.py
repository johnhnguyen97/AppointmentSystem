import json
import os
import subprocess
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
        
        # Login with API key
        login_result = subprocess.run(
            ['bw', 'login', '--apikey', '--raw'],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        
        # Get session key
        session_key = login_result.stdout.strip()
        
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
    Get database credentials from Bitwarden
    
    Returns:
        Dictionary with database connection parameters
    """
    creds = get_bitwarden_credentials("Nail Appointment Database")
    
    # Set defaults for missing values
    creds.setdefault('host', 'localhost')
    creds.setdefault('port', '5432')
    creds.setdefault('database', 'appointment_system')
    
    return creds
