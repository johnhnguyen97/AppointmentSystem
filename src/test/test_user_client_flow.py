from datetime import datetime, timedelta, UTC
from uuid import uuid4
import pytest

from src.main.models import User, Client, ServiceType
from src.main.graphql_context import CustomContext
from src.main.auth import get_password_hash
from src.main.graphql_schema import schema

async def execute_graphql(query, variables=None, context=None):
    return await schema.execute(
        query,
        variable_values=variables,
        context_value=context
    )

@pytest.fixture
async def admin_user(async_session):
    admin = User(
        id=uuid4(),
        username="admin",
        email="admin@example.com",
        password=get_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        enabled=True,
        is_admin=True
    )
    async_session.add(admin)
    await async_session.commit()
    return admin

@pytest.mark.asyncio
async def test_user_client_flow(async_session, admin_user):
    """Test complete flow of user and client creation and updates"""
    
    # 1. Create new user via GraphQL
    create_user_mutation = """
    mutation CreateUser($input: CreateUserInput!) {
        createUser(input: $input) {
            id
            username
            email
            firstName
            lastName
            enabled
        }
    }
    """

    async def get_admin():
        return admin_user

    context = CustomContext(
        session=async_session,
        get_current_user_override=get_admin
    )

    # Create user variables
    user_input = {
        "input": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123",
            "firstName": "Test",
            "lastName": "User",
            "enabled": True
        }
    }

    result = await execute_graphql(
        create_user_mutation,
        variables=user_input,
        context=context
    )
    assert result.errors is None
    assert result.data["createUser"]["username"] == "testuser"
    user_id = result.data["createUser"]["id"]

    # 2. Create client for the new user
    create_client_mutation = """
    mutation CreateClient($input: CreateClientInput!) {
        createClient(input: $input) {
            id
            phone
            service
            status
            notes
            user {
                username
            }
        }
    }
    """

    client_input = {
        "input": {
            "phone": "(555) 123-4567",
            "service": "HAIRCUT",
            "notes": "New client",
            "userId": user_id
        }
    }

    result = await execute_graphql(
        create_client_mutation,
        variables=client_input,
        context=context
    )
    assert result.errors is None
    assert result.data["createClient"]["phone"] == "(555) 123-4567"
    client_id = result.data["createClient"]["id"]

    # 3. Update client information
    update_client_mutation = """
    mutation UpdateClient($id: UUID!, $input: UpdateClientInput!) {
        updateClient(id: $id, input: $input) {
            id
            phone
            service
            status
            notes
        }
    }
    """

    update_input = {
        "id": client_id,
        "input": {
            "phone": "(555) 999-8888",
            "notes": "Updated client info"
        }
    }

    result = await execute_graphql(
        update_client_mutation,
        variables=update_input,
        context=context
    )
    assert result.errors is None
    assert result.data["updateClient"]["phone"] == "(555) 999-8888"
    assert result.data["updateClient"]["notes"] == "Updated client info"

    # 4. Query updated client info
    query_client = """
    query GetClient($id: UUID!) {
        client(id: $id) {
            id
            phone
            service
            status
            notes
            user {
                username
                email
            }
        }
    }
    """

    result = await execute_graphql(
        query_client,
        variables={"id": client_id},
        context=context
    )
    assert result.errors is None
    client_data = result.data["client"]
    assert client_data["phone"] == "(555) 999-8888"
    assert client_data["user"]["username"] == "testuser"

    # 5. Update user information
    update_user_mutation = """
    mutation UpdateUser($id: UUID!, $input: UpdateUserInput!) {
        updateUser(id: $id, input: $input) {
            id
            firstName
            lastName
            email
        }
    }
    """

    update_user_input = {
        "id": user_id,
        "input": {
            "firstName": "Updated",
            "lastName": "Name",
            "email": "updated@example.com"
        }
    }

    result = await execute_graphql(
        update_user_mutation,
        variables=update_user_input,
        context=context
    )
    assert result.errors is None
    assert result.data["updateUser"]["firstName"] == "Updated"
    assert result.data["updateUser"]["email"] == "updated@example.com"
