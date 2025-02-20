import requests
import json

def run_query(query, variables=None, token=None):
    headers = {
        'Content-Type': 'application/json',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
        
    response = requests.post(
        'http://localhost:8000/graphql',
        headers=headers,
        json={'query': query, 'variables': variables}
    )
    return response.json()

# Create user mutation
create_user_mutation = """
mutation {
    createUser(input: {
        username: "test.stylist7"
        email: "test.stylist7@example.com"
        password: "StrongPass123!"
        firstName: "Test"
        lastName: "Stylist"
    }) {
        id
        username
        email
    }
}
"""

# Execute create user
result = run_query(create_user_mutation)
print("Create User Result:")
print(json.dumps(result, indent=2))

# Login mutation
login_mutation = """
mutation {
    login(input: {
        username: "test.stylist7"
        password: "StrongPass123!"
    }) {
        token
        user {
            id
            username
        }
    }
}
"""

# Execute login
login_result = run_query(login_mutation)
print("\nLogin Result:")
print(json.dumps(login_result, indent=2))

if 'data' in login_result and 'login' in login_result['data']:
    token = login_result['data']['login']['token']
    
    # Create client mutation with auth token
    create_client_mutation = """
    mutation CreateClient($userId: UUID!) {
        createClient(input: {
            userId: $userId
            phone: "(555) 123-4567"
            service: HAIRCUT
            status: "active"
            notes: "New client"
        }) {
            id
            phone
            service
            status
            notes
            user {
                id
                username
                email
                firstName
                lastName
            }
        }
    }
    """
    
    # Execute create client with variables
    variables = {
        "userId": login_result['data']['login']['user']['id']
    }
    client_result = run_query(create_client_mutation, variables=variables, token=token)
    print("\nCreate Client Result:")
    print(json.dumps(client_result, indent=2))
