#!/usr/bin/env python3
import asyncio
import json
from uuid import UUID
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# GraphQL queries
CREATE_USER = """
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    username
    email
    firstName
    lastName
  }
}
"""

LOGIN = """
mutation Login($input: LoginInput!) {
  login(input: $input) {
    token
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

CREATE_CLIENT = """
mutation CreateClient($input: CreateClientInput!) {
  createClient(input: $input) {
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

VERIFY_CREATION = """
query VerifyCreation($userId: UUID!) {
  user(id: $userId) {
    id
    username
    email
    firstName
    lastName
  }
  clients {
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

async def main():
    # Initialize the GraphQL client
    transport = AIOHTTPTransport(url='http://localhost:8000/graphql')
    client = Client(transport=transport, fetch_schema_from_transport=True)

    try:
        # 1. Create a new user
        user_variables = {
            "input": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "testpass123",
                "firstName": "John",
                "lastName": "Doe"
            }
        }
        
        user_result = await client.execute_async(
            gql(CREATE_USER),
            variable_values=user_variables
        )
        
        print("\nUser created:")
        print(json.dumps(user_result, indent=2))
        
        # Extract the user ID from the response
        user_id = user_result["createUser"]["id"]
        
        # 2. Login to get authentication token
        login_variables = {
            "input": {
                "username": "johndoe",
                "password": "testpass123"
            }
        }
        
        login_result = await client.execute_async(
            gql(LOGIN),
            variable_values=login_variables
        )
        
        print("\nLogin successful:")
        print(json.dumps(login_result, indent=2))
        
        # Update transport with authentication token
        token = login_result["login"]["token"]
        transport = AIOHTTPTransport(
            url='http://localhost:8000/graphql',
            headers={'Authorization': f'Bearer {token}'}
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # 3. Create a client profile using the user ID
        client_variables = {
            "input": {
                "userId": user_id,
                "phone": "(555) 123-4567",
                "service": "haircut",
                "status": "active",
                "notes": "New client"
            }
        }
        
        client_result = await client.execute_async(
            gql(CREATE_CLIENT),
            variable_values=client_variables
        )
        
        print("\nClient created:")
        print(json.dumps(client_result, indent=2))
        
        # 4. Verify the creation
        verify_variables = {
            "userId": user_id
        }
        
        verify_result = await client.execute_async(
            gql(VERIFY_CREATION),
            variable_values=verify_variables
        )
        
        print("\nVerification result:")
        print(json.dumps(verify_result, indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
