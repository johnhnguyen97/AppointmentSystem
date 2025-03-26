"""
Main GraphQL schema module that composes queries and mutations.
"""
import strawberry
from src.main.queries import Query
from src.main.mutations import AppointmentMutations, ClientMutations, AuthMutations
from typing import Optional, List

@strawberry.type
class Mutation:
    """Root mutation type that combines all mutations."""
    auth: AuthMutations = strawberry.field(
        resolver=lambda: AuthMutations()
    )
    appointments: AppointmentMutations = strawberry.field(
        resolver=lambda: AppointmentMutations()
    )
    clients: ClientMutations = strawberry.field(
        resolver=lambda: ClientMutations()
    )

# Create the schema with both Query and Mutation classes
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
