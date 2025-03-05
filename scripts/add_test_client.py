"""
Script to add a test client using GraphQL mutation
"""
import requests
import json
import sys
import argparse

# GraphQL endpoint
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def login(username, password):
    """Login and get authentication token"""
    print(f"Logging in as {username}...")

    query = """
    mutation Login($input: LoginInput!) {
      login(input: $input) {
        token
        user {
          id
          username
          first_name
          last_name
          is_admin
        }
      }
    }
    """

    variables = {
        "input": {
            "username": username,
            "password": password
        }
    }

    headers = {"Content-Type": "application/json"}
    payload = {"query": query, "variables": variables}

    try:
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

        result = response.json()

        if "data" in result and "login" in result["data"]:
            print("Login successful!")
            print(f"User: {result['data']['login']['user']['username']}")
            print(f"Admin: {result['data']['login']['user']['is_admin']}")
            return result["data"]["login"]["token"]
        else:
            print("Login failed!")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"Error: {error['message']}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def add_client(token, phone, service_type, status="ACTIVE", notes=None, category="NEW"):
    """Add a new client using GraphQL mutation"""
    print(f"Adding client with phone {phone} and service {service_type}...")

    query = """
    mutation AddClient($input: ClientInput!) {
      addClient(input: $input) {
        id
        phone
        service
        status
        notes
        category
        loyalty_points
        total_spent
        visit_count
        last_visit
      }
    }
    """

    variables = {
        "input": {
            "phone": phone,
            "service": service_type,
            "status": status,
            "notes": notes,
            "category": category
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {"query": query, "variables": variables}

    try:
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

        result = response.json()

        if "data" in result and "addClient" in result["data"]:
            print("Client added successfully!")
            print_json(result["data"]["addClient"])
            return result["data"]["addClient"]
        else:
            print("Failed to add client!")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"Error: {error['message']}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_service_types():
    """Get available service types from the GraphQL schema"""
    print("Getting available service types...")

    query = """
    query {
      __type(name: "ServiceType") {
        enumValues {
          name
        }
      }
    }
    """

    headers = {"Content-Type": "application/json"}
    payload = {"query": query}

    try:
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return []

        result = response.json()

        if "data" in result and "__type" in result["data"] and "enumValues" in result["data"]["__type"]:
            enum_values = [value["name"] for value in result["data"]["__type"]["enumValues"]]
            print("Available service types:")
            for value in enum_values:
                print(f"  - {value}")
            return enum_values
        else:
            print("Failed to get service types!")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"Error: {error['message']}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Add a test client using GraphQL mutation")
    parser.add_argument("--username", default="admin", help="Username for login")
    parser.add_argument("--password", default="password", help="Password for login")
    parser.add_argument("--phone", default="(555) 123-4567", help="Client phone number")
    parser.add_argument("--service", help="Service type (if not provided, will use the first available service type)")
    parser.add_argument("--status", default="ACTIVE", choices=["ACTIVE", "INACTIVE", "BLOCKED"], help="Client status")
    parser.add_argument("--notes", help="Additional notes about the client")
    parser.add_argument("--category", default="NEW", choices=["NEW", "REGULAR", "VIP", "PREMIUM"], help="Client category")

    args = parser.parse_args()

    print("Testing GraphQL API...")

    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code != 200:
            print("Server is not running or health check failed!")
            return 1
        print("Server is running!")
    except requests.exceptions.ConnectionError:
        print("Server is not running! Please start the server first.")
        print("Run: ./scripts/start_server.ps1")
        return 1

    # Get available service types
    service_types = get_service_types()
    if not service_types:
        print("No service types available!")
        return 1

    # Use the provided service type or the first available one
    service_type = args.service if args.service else service_types[0]
    if service_type not in service_types:
        print(f"Invalid service type: {service_type}")
        print(f"Available service types: {', '.join(service_types)}")
        return 1

    # Login
    token = login(args.username, args.password)
    if not token:
        return 1

    # Add client
    client = add_client(token, args.phone, service_type, args.status, args.notes, args.category)
    if not client:
        return 1

    print("GraphQL API test completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
