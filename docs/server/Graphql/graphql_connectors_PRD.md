# GraphQL Connectors Guide

## 1. Introduction to Connectors

Apollo Connectors provide a declarative approach to integrate REST APIs into your GraphQL schema. They allow you to:
- Define REST API integrations directly in your schema
- Orchestrate calls across connected APIs
- Transform responses into GraphQL-compatible formats

### Visual Overview
![Connectors Architecture](7370fbc6df9f.svg)

### Key Benefits
1. **API Orchestration**
   - Efficient request coordination
   - Unified response handling
   - Built-in composition support

2. **Developer Experience**
   - Declarative configuration
   - No resolver code needed
   - Automatic request handling

3. **Integration with GraphOS**
   - Security features
   - Scalability support
   - Built-in observability

## 2. Core Concepts

### API Requirements
1. **Content Type**
   - JSON response bodies
   - Optional content type headers
   - Standard HTTP methods

2. **JSON-over-HTTP Principles**
   - Standard HTTP verbs (GET, POST, PUT, PATCH, DELETE)
   - Path segments and query parameters
   - JSON request/response bodies
   - Success status codes (200-299)

3. **Entity Representation**
   - Consistent identifiers
   - Primary key endpoints
   - Simple foreign keys
   - Optional embedded entities

### Security Conventions
1. **Authentication**
   - Header-based auth
   - Endpoint-level security
   - Router security integration

2. **Request Safety**
   - No sensitive query params
   - Protected endpoints
   - Secure header handling

## 3. Making HTTP Requests

### HTTP Methods
```graphql
type Query {
  products: [Product]
    @connect(
      http: { GET: "https://myapi.dev/products" }
      selection: "id"
    )
}

type Mutation {
  createProduct(name: String!): Product
    @connect(
      http: {
        POST: "https://myapi.dev/products"
        body: "name: $args.name"
      }
      selection: "id"
    )
}
```

### Dynamic URLs and Parameters
```graphql
type Query {
  product(storeId: ID!, productId: ID!): Product
    @connect(
      http: {
        GET: "https://myapi.dev/store/{$args.storeId}/products/{$args.productId}"
      }
      selection: "id"
    )
}
```

### Headers
```graphql
type Query {
  products: [Product]
    @connect(
      http: {
        GET: "https://myapi.dev/products"
        headers: [
          { name: "x-api-version", value: "2024-01-01" }
          { name: "Authorization", value: "Bearer {$config.token}" }
        ]
      }
      selection: "id"
    )
}
```

## 4. Response Mapping

### Basic Selection
```graphql
type Query {
  product(id: ID!): Product
    @connect(
      http: { GET: "/products/{$args.id}" }
      selection: """
      id
      name
      description
      """
    )
}
```

### Nested Selection
```graphql
type Query {
  product(id: ID!): Product
    @connect(
      http: { GET: "/products/{$args.id}" }
      selection: """
      id
      variants {
        id
        name
        price
      }
      """
    )
}
```

### Field Renaming
```graphql
type Query {
  product(id: ID!): Product
    @connect(
      http: { GET: "/products/{$args.id}" }
      selection: """
      id: product_id
      title: name
      price: cost
      """
    )
}
```

## 5. Advanced Features

### Configuration Management
```yaml
connectors:
  sources:
    example.v1:
      $config:
        api_key: ${env.API_KEY}
      override_url: "https://api.example.com/v1"
```

### Error Handling
```graphql
type MutationResponse {
  success: Boolean!
  errors: [Error]
}

type Mutation {
  createProduct(input: ProductInput!): MutationResponse
    @connect(
      http: {
        POST: "/products"
        body: "$args.input"
      }
      selection: """
      success
      errors {
        code
        message
      }
      """
    )
}
```

### Authentication
```yaml
authentication:
  connector:
    sources:
      subgraph.source:
        aws_sig_v4:
          default_chain:
            region: "us-east-1"
            service_name: "lambda"
```

## 6. Best Practices

### Design Patterns
1. **Entity-First Approach**
   - Define clear entity boundaries
   - Use consistent identifiers
   - Plan for extensibility

2. **Response Mapping**
   - Keep selections minimal
   - Use clear field names
   - Handle errors gracefully

3. **Configuration**
   - Use environment variables
   - Separate configs by environment
   - Document all config options

### Performance
1. **Request Optimization**
   - Batch requests where possible
   - Use appropriate caching
   - Monitor request limits

2. **Response Handling**
   - Transform data efficiently
   - Handle partial responses
   - Implement proper error states

## 7. Troubleshooting

### Common Issues
1. **Connection Errors**
   - Verify endpoint URLs
   - Check authentication
   - Validate request format

2. **Mapping Errors**
   - Verify selection syntax
   - Check field names
   - Validate response structure

### Debugging Tools
1. **Telemetry**
   - Enable debug logging
   - Monitor request metrics
   - Track error rates

2. **Testing**
   - Use schema validation
   - Test response mappings
   - Verify error handling

## 8. Additional Resources

### Learning Materials
- [Connectors Quickstart](https://www.apollographql.com/docs/graphos/get-started/guides/rest)
- [Interactive Course](https://www.apollographql.com/tutorials/connectors-intro-rest)
- [API Documentation](https://www.apollographql.com/docs/graphos/schema-design/connectors)

### Tools and References
- GraphOS Studio
- Rover CLI
- IDE Plugins
