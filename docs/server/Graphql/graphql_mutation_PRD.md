# GraphQL Mutations Guide

## 1. Core Concepts

Mutations in GraphQL represent operations that:
- Modify server-side data
- Cause side effects on the server
- Can accept parameters
- Can return any field type, including new types and existing object types
- Are useful for fetching new state after updates

## 2. Basic Implementation

### Simple Mutation Example
```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book:
        print(f"Adding {title} by {author}")
        return Book(title=title, author=author)

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### Usage Example
```graphql
mutation {
  addBook(title: "The Little Prince", author: "Antoine de Saint-Exupéry") {
    title
  }
}
```

### Void Mutations
Mutations can be implemented without returning data:
```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def restart() -> None:
        print(f"Restarting the server")
```

Note: Void-result mutations go against GraphQL best practices.

## 3. Input Mutations Pattern

### Using InputMutationExtension
```python
from strawberry.field_extensions import InputMutationExtension

@strawberry.type
class Mutation:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    def update_fruit_weight(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        weight: Annotated[float, strawberry.argument(description="The fruit's new weight in grams")],
    ) -> Fruit:
        fruit = ...  # retrieve the fruit
        fruit.weight = weight
        return fruit
```

Generated Schema:
```graphql
input UpdateFruitWeightInput {
  id: ID!
  weight: Float!  # The fruit's new weight in grams
}

type Mutation {
  updateFruitWeight(input: UpdateFruitWeightInput!): Fruit!
}
```

## 4. Nested Mutations

### Purpose
- Avoid overly large graphs
- Improve discoverability
- Group related mutations by namespace

### Implementation Example
```python
@strawberry.type
class FruitMutations:
    @strawberry.mutation
    def add(self, info, input: AddFruitInput) -> Fruit: ...

    @strawberry.mutation
    def update_weight(self, info, input: UpdateFruitWeightInput) -> Fruit: ...

@strawberry.type
class Mutation:
    @strawberry.field
    def fruit(self) -> FruitMutations:
        return FruitMutations()
```

Generated Schema:
```graphql
type Mutation {
  fruit: FruitMutations!
}

type FruitMutations {
  add(input: AddFruitInput): Fruit!
  updateWeight(input: UpdateFruitWeightInput!): Fruit!
}
```

## 5. Schema Naming Conventions

### General Rules
- Be consistent across the entire schema
- Be specific with names
- Avoid acronyms, initialisms, and abbreviations

### Casing Conventions
- **camelCase**: Field names, argument names, directive names
- **PascalCase**: Type names
- **SCREAMING_SNAKE_CASE**: Enum values

### Field Names
❌ Incorrect:
```graphql
type Query {
  getProducts: [Product]
}
```

✅ Correct:
```graphql
type Query {
  products: [Product]
}
```

### Type Names
- Use suffix `Input` for input types
- Use consistent suffix (`Response` or `Payload`) for mutation outputs

### Namespacing Conventions
When resolving naming conflicts between domains:

1. PascalCase prefix:
```graphql
type StoreCustomer { ... }
type SiteCustomer { ... }
```

2. Single_Underscore prefix:
```graphql
type Store_Customer { ... }
type Site_Customer { ... }
```

## 6. Serial Execution

### Root-Level Mutations
- Must be resolved serially
- Helps prevent race conditions
- Follows GraphQL specification

### Namespace Mutations
- Are resolved in parallel by default
- Can be serialized using client-side aliases

Example of serial execution with aliases:
```graphql
mutation DoTwoNestedThingsInSerial(
  $createInput: CreateReviewInput!
  $deleteInput: DeleteReviewInput!
) {
  a: reviews {
    create(input: $createInput) {
      success
    }
  }
  b: reviews {
    delete(input: $deleteInput) {
      success
    }
  }
}
```

## 7. Best Practices

1. **Error Handling**
   - Implement proper error handling in real-world applications
   - Consider returning union types for error states

2. **Input Types**
   - Use single input type arguments when possible
   - Leverage InputMutationExtension for clean input handling

3. **Naming**
   - Follow consistent naming conventions
   - Use clear, descriptive names
   - Start mutation names with verbs

4. **Structure**
   - Consider using namespaces for related mutations
   - Be mindful of serial vs parallel execution
   - Follow GraphQL specification requirements
