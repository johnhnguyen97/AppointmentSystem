"""
Script to demonstrate how to create a client with the correct service type
"""
import requests
import json

# GraphQL endpoint
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def login(username, password):
    """Login and get authentication token"""
    print(f"Logging in as {username}...")

    query = """
    mutation {
      login(input: {username: "%s", password: "%s"}) {
        token
        user {
          id
          username
          firstName
          lastName
          isAdmin
        }
      }
    }
    """ % (username, password)

    headers = {"Content-Type": "application/json"}
    payload = {"query": query}

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
            print(f"Admin: {result['data']['login']['user']['isAdmin']}")
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

def create_client(token, phone, service_type, notes=None):
    """Create a client with the correct service type"""
    print(f"Creating client with phone {phone} and service {service_type}...")

    # This is the key part - we need to use the raw GraphQL query with the service type as a string
    # but wrapped in quotes to make it a string literal in the GraphQL query
    query = """
    mutation {
      create_client(input: {
        phone: "%s",
        service: %s,
        notes: "%s"
      }) {
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
    """ % (phone, service_type, notes or "")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {"query": query}

    try:
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

        result = response.json()

        if "data" in result and "create_client" in result["data"]:
            print("Client created successfully!")
            print_json(result["data"]["create_client"])
            return result["data"]["create_client"]
        else:
            print("Failed to create client!")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"Error: {error['message']}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main function"""
    print("Testing GraphQL API...")

    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code != 200:
            print("Server is not running or health check failed!")
            return
        print("Server is running!")
    except requests.exceptions.ConnectionError:
        print("Server is not running! Please start the server first.")
        print("Run: ./scripts/start_server.ps1")
        return

    # Login
    token = login("admin", "password")
    if not token:
        return

    # Create client with HAIRCUT service type
    # Note: We're passing the service type as a string literal in the GraphQL query
    client = create_client(
        token=token,
        phone="(555) 123-4567",
        service_type="HAIRCUT",  # This will be inserted as a string literal in the GraphQL query
        notes="New client added via Python script"
    )

    if client:
        print("Client created successfully!")
    else:
        print("Failed to create client!")

if __name__ == "__main__":
    main()
