# GraphQL Schema Design Guide

## 1. Schema Fundamentals

### What is a GraphQL Schema?
- Describes the shape of available data
- Defines a hierarchy of types with fields
- Specifies available queries and mutations
- Controls which operations clients can execute

### Schema Definition Approaches
1. **Schema-first**: Uses Schema Definition Language (SDL)
2. **Code-first**: Uses programming language constructs (Strawberry's approach)

## 2. Core Types

### Scalar Types
- **Basic Types**:
  - `Int`: 32-bit integer
  - `Float`: Double-precision floating-point
  - `String`: UTF-8 character sequence
  - `Boolean`: true/false
  - `ID`: Unique identifier
  - `UUID`: UUID value serialized as string

- **Additional Types** (Strawberry-specific):
  - `Date`
  - `Time`
  - `DateTime` (ISO-8601 format)

### Object Types
```python
@strawberry.type
class Book:
    title: str
    author: "Author"

@strawberry.type
class Author:
    name: str
    books: typing.List[Book]
```

### The Query Type
```python
@strawberry.type
class Query:
    books: typing.List[Book]
    authors: typing.List[Author]
```

### The Mutation Type
```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book:
        ...
```

### Input Types
```python
@strawberry.input
class AddBookInput:
    title: str = strawberry.field(description="The title of the book")
    author: str = strawberry.field(description="The name of the author")
```

## 3. Data Handling Techniques

### Field Resolvers
```python
def get_author_for_book(root) -> "Author":
    return Author(name="Michael Crichton")

@strawberry.type
class Book:
    title: str
    author: "Author" = strawberry.field(resolver=get_author_for_book)
```

### Data Patterns
1. **Basic Value Resolution**
   - Direct field mapping
   - Simple computations
   - Type transformations

2. **Database Integration**
   - ORM integration
   - Raw SQL queries
   - Connection pooling
   ```python
   async def get_user(self, info) -> User:
       async with info.context["db"].acquire() as conn:
           result = await conn.fetch_one("SELECT * FROM users WHERE id = $1", self.id)
           return User(**result)
   ```

3. **External API Integration**
   - REST API calls
   - Microservice communication
   - Third-party service integration
   ```python
   async def get_weather(self, info) -> WeatherData:
       async with httpx.AsyncClient() as client:
           response = await client.get(f"https://api.weather.com/{self.city}")
           return WeatherData(**response.json())
   ```

4. **Caching Strategies**
   - In-memory caching
   - Distributed caching
   - Cache invalidation
   ```python
   @strawberry.field
   async def cached_data(self, info) -> Data:
       cache_key = f"data:{self.id}"
       if cached := await info.context["cache"].get(cache_key):
           return Data(**cached)
       data = await fetch_fresh_data()
       await info.context["cache"].set(cache_key, data.dict())
       return data
   ```

5. **Batch Loading**
   - DataLoader implementation
   - N+1 query prevention
   ```python
   async def load_books_by_author(self, keys):
       books = await db.fetch("SELECT * FROM books WHERE author_id = ANY($1)", keys)
       return [books_by_author[key] for key in keys]
   ```

### Field Definition Patterns
```graphql
type Book {
  title: String!         # Required field
  author: Author        # Nullable relation
  ratings: [Int]        # List field
  price: Float          # Computed field
  metadata: JSON        # Custom scalar
}
```

### Error Handling
1. **Type-Safe Errors**
   ```python
   @strawberry.type
   class Error:
       message: str
       code: str

   @strawberry.type
   class UserResult:
       user: Optional[User]
       error: Optional[Error]
   ```

2. **Union Types for Results**
   ```python
   @strawberry.type
   class SuccessResult:
       data: Data

   @strawberry.type
   class ErrorResult:
       error: str

   Result = strawberry.union("Result", [SuccessResult, ErrorResult])
   ```

### Performance Optimization
1. **Selective Loading**
   - Field-level resolvers
   - Lazy loading
   - Conditional fetching

2. **Connection Pattern**
   ```graphql
   type BookConnection {
     edges: [BookEdge]
     pageInfo: PageInfo!
   }

   type BookEdge {
     node: Book!
     cursor: String!
   }
   ```

## 4. Advanced Patterns

### Namespacing
```graphql
type UsersMutations {
  create(profile: UserProfileInput!): User!
  block(id: ID!): User!
}

type Mutation {
  users: UsersMutations!
}
```

### Server-Driven UI

#### Core Structure
```graphql
type UIComponent {
  id: ID!
  type: String!
  props: JSON
  children: [UIComponent!]
}

type Query {
  getPageLayout(page: String!): [UIComponent!]!
}
```

#### Device-Specific Components
```graphql
enum UIDeviceType {
  MOBILE
  WEB
  ROKU
  APPLETV
}

type Query {
  app(type: UIDeviceType! = WEB): UIApp!
}
```

## 5. Schema Development and Evolution

### Schema Versioning
1. **Breaking vs Non-Breaking Changes**
   - Breaking: Removing fields, changing types
   - Non-Breaking: Adding fields, deprecating fields
   - Guidance on managing changes

2. **Deprecation Strategy**
   ```graphql
   type User {
     id: ID!
     name: String!
     email: String @deprecated(reason: "Use `contactInfo.email` instead")
     contactInfo: ContactInfo!
   }
   ```

### Schema Growth Patterns
1. **Additive Changes**
   - Adding new fields
   - Extending existing types
   - Creating new types
   ```graphql
   extend type User {
     preferences: UserPreferences
     settings: UserSettings
   }
   ```

2. **Type Evolution**
   - Interface extensions
   - Union type additions
   - Enum expansions
   ```graphql
   interface Node {
     id: ID!
   }

   interface Timestamped {
     createdAt: DateTime!
     updatedAt: DateTime
   }

   type User implements Node & Timestamped {
     id: ID!
     createdAt: DateTime!
     updatedAt: DateTime
     # ... other fields
   }
   ```

### Schema Management
1. **Documentation**
   - Schema changelog
   - Deprecation notices
   - Migration guides
   ```graphql
   """
   User account information
   @changelog:
   - 2025-03: Added contactInfo field
   - 2025-02: Deprecated email field
   """
   type User {
     # ...
   }
   ```

2. **Testing Strategies**
   - Schema validation tests
   - Breaking change detection
   - Client query validation
   ```python
   @pytest.mark.schema
   def test_breaking_changes():
       diff = compare_schemas(old_schema, new_schema)
       assert not diff.has_breaking_changes
   ```

3. **Schema Review Process**
   - Impact analysis
   - Client compatibility checks
   - Version control integration
   ```yaml
   # schema-review.yaml
   checks:
     - breaking-changes
     - complexity-limits
     - naming-conventions
   notify:
     - client-teams
     - api-owners
   ```

### Backwards Compatibility
1. **Maintaining Compatibility**
   - Field aliasing
   - Type wrapping
   - Default values
   ```graphql
   type Query {
     # Old field maintained for compatibility
     user(id: ID!): User
     # New field with enhanced capabilities
     userById(input: UserQueryInput!): UserResult!
   }
   ```

2. **Migration Support**
   - Dual running periods
   - Usage monitoring
   - Client coordination
   ```graphql
   type Mutation {
     # Support both old and new formats
     updateUser(
       id: ID!
       input: UserUpdateInput
       # Old fields maintained but deprecated
       name: String @deprecated
       email: String @deprecated
     ): User!
   }
   ```

## 6. Best Practices

### Schema Design
1. **Query-Driven Development**
   - Design based on use cases
   - Focus on client requirements
   - Avoid unnecessary exposure

2. **Type Naming**
   - Use PascalCase for types
   - Use camelCase for fields
   - Be descriptive and consistent

3. **Documentation**
   - Add field descriptions
   - Include examples
   - Document changes

### Performance
1. **Optimization**
   - Use dataloaders
   - Implement caching
   - Monitor performance

2. **Field Selection**
   - Request only needed fields
   - Use fragments
   - Consider complexity

# Mocking to Unblock Development

As your organization builds out its A unified, federated graph composed of separate GraphQL APIs using Apollo Federation. Enables a microservices architecture that exposes a unified GraphQL API to clients.[Learn more about federation.](https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/federation) you might discover that your client teams are often waiting on A service in a federated GraphQL architecture. Acts as a module for a supergraph. Includes both GraphQL services and REST services integrated via Apollo Connectors.[Learn more about supergraphs and subgraphs.](https://www.apollographql.com/docs/graphos/get-started/concepts/graphs#supergraphs) owners to make agreed-upon changes to their schemas. During this time, you can *mock* parts of your supergraph as you develop both your clients and subgraphs, enabling teams to work in parallel without blocking each other.

## First, agree on your schema

To mock parts of your supergraph effectively, both client and backend teams need to agree on the structure of those parts as part of a larger governance strategy and approval process. Alignment between these teams on schema additions/removals/changes can help make your schema more useful and expressive.

We recommended that your backend and client teams align on your schema's structure ahead of time, even if you don't use schema mocking. Doing so enables you to create an expressive schema that accelerates all teams.

### Creating a new schema

If you're creating an entirely new An interconnected set of data represented by a schema. It encompasses the relationships between different data types and how they can be queried or mutated.[Learn more about GraphQL.](https://graphql.com/learn/what-is-graphql/) and corresponding schema, it's important first to familiarize yourself with schema best practices, such as those described in [Apollo Odyssey](https://www.apollographql.com/tutorials), [Principled GraphQL](https://principledgraphql.com/), and the [Supergraph Architecture Framework](https://www.apollographql.com/docs/graphos/reference/saf).

For new schemas, we recommend using [this sample by GitHub user setchy](https://github.com/setchy/apollo-server-4-mocked-federation) to mock your new schema in its entirety. This provides your client teams with a local (or hosted) instance of the schema to query against and begin mocking UI components with the mocked data.

To use this sample, you need to [publish your schema to Apollo GraphOS](https://www.apollographql.com/docs/graphos/platform/schema-management/delivery/publish). For details on the benefits of publishing to A platform for building and managing a supergraph. It provides a management plane to test and ship changes and runtime capabilities to secure and monitor the graph.[Learn more about GraphOS.](https://www.apollographql.com/docs/graphos/get-started/concepts/graphos) [see below](https://www.apollographql.com/docs/graphos/schema-design/guides/mocking.md#why-use-graphos-for-a-mocked-server).

To get started with the sample, run the following:

```bash
git clone https://github.com/setchy/apollo-server-4-mocked-federation
cd apollo-server-4-mocked-federation
npm install
cp .env.template .env
```

Then, edit the `.env` file with the appropriate values from The web interface for GraphOS, which provides graph, variant, and organization management, metrics visualization, schema pipeline tools and more.[Visit GraphOS Studio.](https://studio.apollographql.com/) and run the following to start the server:

```bash
npm run dev
```

The sample uses the `@graphql-tools/mock` package to power the mocks. You can customize the sample's behavior by following the instructions in the [package's documentation page](https://www.the-guild.dev/graphql/tools/docs/mocking).

This gateway can then be used either locally (such as for local client development) or as a hosted gateway internally to be used by client developers.

The data is mocked, however it doesn't require any work from server teams to support and will match the schema as it exists within GraphOS Studio. As we're using GraphOS Studio for the schema, schema changes will automatically be pulled ensuring client developers are working on the latest version.

### Modifying an existing schema

The process for making changes to an existing schema is similar to that for creating a new one, especially in terms of planning. As you add new features, it's important reach a design consensus early, especially for features that require extensive backend work (for example, machine learning).

To mock proposed changes (such as adding a new type/field), we recommend using [this sample created by Apollo's Solutions Architecture team](https://github.com/apollosolutions/apollo-faker-demo). This sample requires a preexisting GraphQL API to be running. It works by allowing for a "patched" or modified version of your subgraph to run locally with mocked data, while using the remote API for all other data.

You'll need to [publish your schema to GraphOS](https://www.apollographql.com/docs/graphos/platform/schema-management/delivery/publish) to use this sample. For details on the benefits of publishing to GraphOS, [see below](https://www.apollographql.com/docs/graphos/schema-design/guides/mocking.md#why-use-graphos-for-a-mocked-server).

To get started, run:

```graphql
mkdir mocked_gateway
export APOLLO_KEY=key_from_studio #replace with the actual key from GraphOS Studio
cd mocked_gateway
touch proposed.graphql
npx github:@apollosolutions/apollo-faker-demo --graphref <yourgraph>@<variant> --remote https://yourapi.com/graphql
```

Then, modify the `proposed.graphql` file with the proposed changes. There are configuration options available via the `@graphql-tools/mock` package, and you can set these options as documented in [the sample's README file, under step 5](https://github.com/apollosolutions/apollo-faker-demo#usage).

## Why use GraphOS for a mocked server?

Now that you have either a new schema or changes to an existing one, it's important to publish that schema to A platform for building and managing a supergraph. It provides a management plane to test and ship changes and runtime capabilities to secure and monitor the graph.[Learn more about GraphOS.](https://www.apollographql.com/docs/graphos/get-started/concepts/graphos) for the following reasons:

* GraphOS Studio provides a centralized view of your schema, along with a [mocked view of the schema](https://www.apollographql.com/docs/graphos/explorer/additional-features/#mocked-responses).
* By publishing to GraphOS, the samples referenced above can automatically update on changes, allowing for a deployed version of the samples to be referenced by all developers.
* For client teams using code generation tools (especially those in Apollo's client libraries) it's possible to use GraphOS as a source of the schema, allowing for more straightforward development.

We recommend using a Independent instances of a graph often used to represent different environments. Each variant has its own schema and own router.[Learn more about variants.](https://www.apollographql.com/docs/graphos/platform/graph-management/variants) of your new/existing production graph ID. If considering mocking for schema changes, this also ensures proposed changes aren't breaking using [schema checks](https://www.apollographql.com/docs/graphos/platform/schema-management/checks) against production traffic.

# Schema Deprecations

If you're an enterprise customer looking for more material on this topic, try the [Enterprise best practices: Schema design](https://www.apollographql.com/tutorials/schema-design-best-practices) course on Apollo's official learning platform, featuring interactive tutorials, videos, code challenges, and certifications.[Visit Odyssey.](https://www.apollographql.com/tutorials/)

Not an enterprise customer? [Learn about GraphOS for Enterprise.](https://www.apollographql.com/pricing?referrer=docs-content)

## Leverage SDL and tooling to manage deprecations

Your An interconnected set of data represented by a schema. It encompasses the relationships between different data types and how they can be queried or mutated.[Learn more about GraphQL.](https://graphql.com/learn/what-is-graphql/) governance group should outline a company-wide field rollover strategy to gracefully handle type and field deprecations throughout the unified graph.

GraphQL APIs can be versioned, but at Apollo, we have seen that it is far more common for organizations to leverage GraphQL's inherently evolutionary nature and iterate their APIs on a rapid and incremental basis. Doing so, however, requires clear communication with API consumers, and especially when field deprecations are required.

## Use the `@deprecated` type system directive

As a first step, the `@deprecated` A GraphQL annotation for a schema or operation that customizes request execution. Prefixed with `@` and may include arguments. For example, the `@lowerCase` directive below can define logic to return the `username` field in lowercase:```graphql
type User {
  username: String! @lowerCase
}
```[Learn more about directives.](https://www.apollographql.com/docs/apollo-server/schema/directives/) which is [defined in the GraphQL specification](https://spec.graphql.org/October2021/#sec--deprecated), should be applied when deprecating fields or enum values in a schema. Its single `reason` argument can also provide the API consumer some direction about what to do instead of using that field or enum value. For instance, this example we can indicate that a related `topProducts` query has been deprecated as follows:

```graphql
extend type Query {
  """
  Fetch a simple list of products with an offset
  """
  topProducts(
    "How many products to retrieve per page."
    first: Int = 5
  ): [Product] @deprecated(reason: "Use `products` instead.")

  """
  Fetch a paginated list of products based on a filter type.
  """
  products(
    "How many products to retrieve per page."
    first: Int = 5
    "Begin paginating results after a product ID."
    after: Int = 0
    "Filter products based on a type."
    type: ProductType = LATEST
  ): ProductConnection
}
```

## Use field usage metrics to assess when it's safe to remove fields

After a service's schema has been updated with new `@deprecated` directives, it's important to communicate the deprecations beyond the GraphQL's schema definition language (SDL). The syntax for writing GraphQL schemas. All GraphQL APIs can use SDL to represent their schema, regardless of the API's programming language.[Learn about SDL in Odyssey.](https://www.apollographql.com/tutorials/lift-off-part1/v1/03-schema-definition-language-sdl#-the-graphql-schema) as well. Using a A legacy Apollo plan that lets you run a cloud router on dedicated, pre-provisioned infrastructure that you control and scale.[Browse plans.](https://www.apollographql.com/pricing) Slack channel or team meetings might serve as appropriate communication channels for such notices, and they should be delivered with any additional migration instructions for client teams.

At this point, a crucial question still remains: "When will it be safe to remove the deprecated field?" To answer this question with certainty that you won't cause any breaking changes to client applications, you must lean on your observability tooling.

Specifically, the [**Clients & Operations** table](https://www.apollographql.com/docs/graphos/platform/insights/field-usage#field-details) on the **Insights** page in [GraphOS Studio](https://studio.apollographql.com/) can provide insight into what clients might still be using the deprecated fields.

In addition, [schema checks](https://www.apollographql.com/docs/graphos/platform/schema-management/checks) will check any changes pushed for registered schemas against a recent window of operation tracing data to ensure that a deprecated field rollover can be completed without causing any breaking changes to existing clients. It's common to [require that clients identify themselves](https://www.apollographql.com/docs/graphos/routing/observability/client-id-enforcement) so that you can reach out to them before making a breaking change.

# Mutation Management with Apollo Federation

Understand the basics of [Apollo Federation](https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/federation) and federated An interconnected set of data represented by a schema. It encompasses the relationships between different data types and how they can be queried or mutated.[Learn more about GraphQL.](https://graphql.com/learn/what-is-graphql/)

Apollo’s implementation of GraphQL Federation—an architecture for orchestrating multiple APIs into a single GraphQL API.[Learn more about Apollo Federation.](https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/federation) is a powerful system for orchestrating queries across a distributed system. For example, you can use Federation to:

* Query data from multiple systems in parallel
* Sequence calls to multiple systems when there are dependencies between them via [`@key` and `@requires` directives](https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/entities/contribute-fields#using-requires-with-object-subfields)
* Orchestrate any combination of parallel and sequential calls to multiple systems
* Batch calls to a single system to [solve the infamous N+1 problem](https://www.apollographql.com/docs/graphos/schema-design/guides/handling-n-plus-one)
* Split a single call into multiple calls with different priorities [using `@defer`](https://www.apollographql.com/docs/graphos/routing/operations/defer)

Federation applies these same capabilities to mutation fields (and their The part of a GraphQL query that specifies the fields and subfields to retrieve from the server. Selection sets define the structure and shape of the data response.The following example query has four selection sets:```graphql
query GetWeatherForecast {
  weatherForecast {
    currentConditions {
      conditions
      temperature
    }
    dailyForecast {
      highTemperature
      lowTemperature
      conditions
    }
    timestamp
  }
}
```The root selection set contains the `weatherForecast` field. `weatherForecast` has its own selection set with three fields. Two of those fields—`currentConditions` and `dailyForecast`— contain selection sets themselves.[Read more in the GraphQL Specification.](https://spec.graphql.org/October2021/#sec-Selection-Sets) but managing state changes across distributed systems typically involves additional requirements. Federation does not provide common functionality for these requirements, such as compensating transactions or data propagation between sibling fields.

You need to implement your own logic within a single field A function that populates data for a particular field in a GraphQL schema. For example:```js
const resolvers = {
  Query: {
    author(root, args, context, info) {
      return find(authors, { id: args.id });
    },
  },
};
```[Learn more about resolvers.](https://www.apollographql.com/docs/apollo-server/data/resolvers/) to implement these requirements. This is due to the design of GraphQL itself.

## Sequencing mutations in GraphQL

The only difference between the root `Query` and `Mutation` types is that [mutation fields are executed serially instead of in parallel](https://spec.graphql.org/October2021/#sec-Normal-and-Serial-Execution). At first glance, this seems like a way to sequence a set of related mutations.

```graphql
mutation DoMultipleThings {
  createAccount {
    success
    account {
      id
    }
  }
  validateAccount {
    success
  }
  setAccountStatus {
    success
  }
}
```

The GraphQL spec ensures that `validateAccount` and `setAccountStatus` will not execute if `createAccount` fails. At first glance, this seems like a way to transactionally execute a set of mutations, but it has some significant downsides:

* We don't have a way to roll back the changes made by `createAccount` if one of `validateAccount` or `setAccountStatus` fails.
* We don't have a way to propagate data between mutations. For example, if `Mutation.createAccount` returns a `Account` with an `id`, we can't use that `id` in `validateAccount` or `setAccountStatus`.
* Clients have to contend with a number of failure scenarios by inspecting the `success` field of each mutation and determining the appropriate course of action.

Even if all three of these mutations are implemented in the same service, it's difficult to implement the appropriate transactional semantics when run within the GraphQL execution engine. We should instead implement this operation as a single mutation resolver so that we can handle failures and rollbacks in one function.

In this JavaScript example, we're implementing a simplistic ["saga"](https://microservices.io/patterns/data/saga.html) that orchestrates state changes across multiple systems.

```js
const resolvers = {
  Mutation: {
    async createAndValidateAccount() {
      const account = createAccount();

      try {
        validate(account);
        setAccountStatus(account, 'ACTIVE');
      } catch (e) {
        deleteAccount(account);
        return {success: false};
      }

      return {success: true, account};
    }
  }
};
```

By representing this operation in a single field, we can properly handle failure, rollback, and data propagation in one function. We also remove complex error management from our client applications and our schema more clearly expresses the client intent.

## Best practices for distributed systems

What if the state changes occur in different services? Because GraphQL and Federation do not provide semantics for distributed transactions, we still need to implement orchestration logic within a single field.

This requirement leads to a few challenging questions:

* Which team or domain owns this mutation field?
* In which A service in a federated GraphQL architecture. Acts as a module for a supergraph. Includes both GraphQL services and REST services integrated via Apollo Connectors.[Learn more about supergraphs and subgraphs.](https://www.apollographql.com/docs/graphos/get-started/concepts/graphs#supergraphs) service should we implement the resolver?
* How does the resolver communicate with the data services?

There are no universally correct answers to these questions. Your answers will depend on your organization, your product requirements, and the capabilities of your system.

One potential strategy is to create one or more subgraphs specifically for orchestrating mutations. These subgraphs can communicate with data services using REST or RPC. Experience or product teams are often the most appropriate owners of these subgraphs.

It's tempting to have the orchestrating subgraph resolvers call back to the A scalable runtime for supergraphs that's fully integrated with GraphOS and based on the Apollo Router Core. Can be cloud- or self-hosted.[Learn more about routing.](https://www.apollographql.com/docs/graphos/routing/about-router) to execute domain-specific mutations. This approach is feasible, but it requires careful attention to a number of details:

* All calls should go through the The single access point for a federated GraphQL architecture. It receives incoming operations and intelligently routes them across component services before returning a unified response.[Learn more about routing.](https://www.apollographql.com/docs/graphos/routing) not directly to subgraphs, because it's responsible for tracking GraphQL usage (and [subgraphs should never accept traffic directly](https://www.apollographql.com/docs/graphos/platform/security/overview#allow-only-the-router-to-query-subgraphs).)
* The calls to domain-specific mutations no longer originate in client applications, so you must propagate client identity and other request metadata.
* A platform for building and managing a supergraph. It provides a management plane to test and ship changes and runtime capabilities to secure and monitor the graph.[Learn more about GraphOS.](https://www.apollographql.com/docs/graphos/get-started/concepts/graphos) will view these calls as separate operations.
* If using cloud-native telemetry, you must ensure that the router receives the trace context to correlate spans.
* Be wary of circular dependencies. Consider using [contracts](https://www.apollographql.com/docs/graphos/platform/schema-management/delivery/contracts/overview) to create Independent instances of a graph often used to represent different environments. Each variant has its own schema and own router.[Learn more about variants.](https://www.apollographql.com/docs/graphos/platform/graph-management/variants) that expose only the domain-specific mutations and eliminate the potential for loops in an operation.

Read more on [contracts usage patterns](https://www.apollographql.com/docs/graphos/platform/schema-management/delivery/contracts/usage-patterns).

If you're an enterprise customer looking for more material on this topic, try the [Enterprise best practices: Contracts](https://www.apollographql.com/tutorials/contracts) course on Apollo's official learning platform, featuring interactive tutorials, videos, code challenges, and certifications.[Visit Odyssey.](https://www.apollographql.com/tutorials/)

Not an enterprise customer? [Learn about GraphOS for Enterprise.](https://www.apollographql.com/pricing?referrer=docs-content)
