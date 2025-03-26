# GraphQL Code Generation Guide

## 1. Overview

Strawberry provides code generation capabilities for:
- Converting SDL (Schema Definition Language) files to Python code
- Generating type-safe code from GraphQL queries
- Supporting custom plugins for extended functionality

## 2. Schema Code Generation

### Basic Usage
```bash
strawberry schema-codegen schema.graphql
```

### Example
Input SDL:
```graphql
type Query {
  user: User
}

type User {
  id: ID!
  name: String!
}
```

Generated Python code:
```python
import strawberry

@strawberry.type
class Query:
    user: User | None

@strawberry.type
class User:
    id: strawberry.ID
    name: str

schema = strawberry.Schema(query=Query)
```

## 3. Query Code Generation

### Purpose
- Generate types for clients using GraphQL APIs
- Provide type safety without external tools
- Similar functionality to GraphQL Codegen but integrated with Strawberry

### Example Schema
```python
from typing import List
import strawberry

@strawberry.type
class Post:
    id: strawberry.ID
    title: str

@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: str

    @strawberry.field
    def post(self) -> Post:
        return Post(id=self.id, title=f"Post for {self.name}")

@strawberry.type
class Query:
    @strawberry.field
    def user(self, info) -> User:
        return User(id=strawberry.ID("1"), name="John", email="abc@bac.com")

    @strawberry.field
    def all_users(self) -> List[User]:
        return [
            User(id=strawberry.ID("1"), name="John", email="abc@bac.com"),
        ]

schema = strawberry.Schema(query=Query)
```

### Example Query
```graphql
query MyQuery {
  user {
    post {
      title
    }
  }
}
```

### Generate Types
Command:
```bash
strawberry codegen --schema schema --output-dir ./output -p python query.graphql
```

Generated Output (`output/query.py`):
```python
class MyQueryResultUserPost:
    title: str

class MyQueryResultUser:
    post: MyQueryResultUserPost

class MyQueryResult:
    user: MyQueryResultUser
```

## 4. Plugin System

### Basic Usage
Multiple plugins can be used:
```bash
strawberry codegen --schema schema --output-dir ./output -p python -p typescript query.graphql
```

### Custom Plugin Interface
```python
from strawberry.codegen import CodegenPlugin, CodegenFile, CodegenResult
from strawberry.codegen.types import GraphQLType, GraphQLOperation

class QueryCodegenPlugin:
    def __init__(self, query: Path) -> None:
        self.query = query

    def on_start(self) -> None:
        """Called before codegen starts"""
        pass

    def on_end(self, result: CodegenResult) -> None:
        """Called after codegen ends"""
        pass

    def generate_code(
        self, types: List[GraphQLType], operation: GraphQLOperation
    ) -> List[CodegenFile]:
        """Generate code for types and operations"""
        return []
```

### Console Plugin
The Console plugin helps orchestrate the codegen process:

```python
class ConsolePlugin:
    def __init__(self, output_dir: Path):
        """Initialize with output directory"""
        pass

    def before_any_start(self) -> None:
        """Called before any plugins start"""
        pass

    def after_all_finished(self) -> None:
        """Called after all codegen is complete"""
        pass

    def on_start(self, plugins: Iterable[QueryCodegenPlugin], query: Path) -> None:
        """Called before individual plugins start"""
        pass

    def on_end(self, result: CodegenResult) -> None:
        """Persists results to output directory"""
        pass
```

## 5. Best Practices

1. **Output Organization**
   - Use consistent output directories
   - Maintain clear separation between generated files
   - Consider version control implications

2. **Plugin Selection**
   - Choose appropriate plugins for your use case
   - Consider using multiple plugins when needed
   - Custom plugins for specific requirements

3. **Code Generation Management**
   - Regularly update generated code
   - Include generation commands in build processes
   - Document code generation steps

4. **Type Safety**
   - Leverage generated types in client code
   - Validate queries against schema
   - Keep generated types in sync with schema changes
