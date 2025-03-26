# Product Requirements Document (PRD)

## Project Overview
**Product Name:** Booking Appointment System
**Objective:** Develop a fully functional booking system with user management, appointment scheduling, inventory management, and a dashboard. The system will use Apollo GraphQL Client with Angular and TypeScript for the frontend. The backend will utilize FastAPI with Strawberry GraphQL and SQLAlchemy for data persistence. The project will be managed using Poetry and `pyproject.toml`, with dependencies encapsulated in a virtual environment (`venv`).

---

## System Architecture
### **Frontend (Angular & Apollo GraphQL Client)**
- **Framework:** Angular (TypeScript) with Apollo GraphQL Client.
- **GraphQL Integration:** Apollo Client for handling queries, mutations, and subscriptions.
- **State Management:** Apollo Cache or Angular state management solutions.
- **Component Structure:**
  - Dashboard (overview metrics and user actions)
  - Clients List (CRUD operations for clients)
  - Inventory List (Manage stock levels)
  - Appointment List (Scheduling with calendar grid system)
  - Settings (Configurations and user preferences)
- **Future Plan:** Transition to React with JavaScript.

### **Backend (FastAPI & Strawberry GraphQL)**
- **Framework:** FastAPI.
- **GraphQL Library:** Strawberry GraphQL.
- **Database:** SQLAlchemy with async support.
- **Virtual Environment:** `venv` for dependency isolation.
- **Dependency Management:** Poetry (`pyproject.toml`).
- **Backend Structure:**
  - **Auth** (Authentication & Authorization setup)
  - **Config** (Application settings and environment configurations)
  - **Database** (SQLAlchemy models and migrations)
  - **GraphQL Context** (Middleware handling request and user authentication)
  - **GraphQL Schema** (Queries and Mutations)
  - **Models** (SQLAlchemy models)
  - **Schema** (GraphQL Schema for data interaction)
  - **Server** (FastAPI server entry point)
  - **Typing** (Type definitions for clarity and consistency)
  - **Test Folder** (Unit tests for API, authentication, and data models)

---

## Functional Requirements
### **User Management**
- Register, login, and role-based access control (Admin, Staff, Clients).
- User profile management.

### **Appointments**
- Create, update, and cancel appointments.
- Calendar grid system integration.

### **Clients Management**
- CRUD operations for client data.

### **Inventory Management**
- Track and manage stock levels.

### **Settings**
- User preferences and system configurations.

### **GraphQL API Requirements**
- Queries for fetching data (Appointments, Clients, Inventory, Users).
- Mutations for data modifications.
- Authentication and authorization middleware.
- Subscription for real-time updates (if needed).

---

## Technical Requirements
- **Database:** PostgreSQL with SQLAlchemy ORM.
- **Testing:** Pytest for backend testing.
- **API Documentation:** Auto-generated via FastAPI.
- **Code Formatting:** Black & isort.
- **Security:** JWT-based authentication.
- **Version Control:** Git & GitHub for repository management.
- **Deployment:** Future deployment considerations (Docker, Cloud services).

---

## GraphQL API Standards

### Authentication & Authorization
- Authentication must happen before GraphQL request validation
- Authorization should occur within business logic during request execution
- Authorization logic should be delegated to business logic layer, not GraphQL layer
- User identity should be passed via context object

**Recap:**
- Keep authentication/authorization separate from GraphQL logic
- Use consistent business layer authorization
- Pass user context appropriately

### Pagination
- Implement cursor-based pagination for list fields
- Use connection pattern with edges and nodes
- Include totalCount and pageInfo in connection types
- Support first/after parameters for forward pagination

**Example Connection Type:**
```graphql
type AppointmentConnection {
  totalCount: Int
  edges: [AppointmentEdge]
  appointments: [Appointment]
  pageInfo: PageInfo!
}

type PageInfo {
  startCursor: ID
  endCursor: ID
  hasNextPage: Boolean!
}
```

**Recap:**
- Use cursor-based pagination consistently
- Include connection metadata
- Follow Relay connection specification

### Schema Design
- Use globally unique IDs for objects
- Design schema based on how data is used rather than stored
- Make fields nullable by default unless guaranteed
- Provide clear error information via standard format

**Recap:**
- Focus on client usage patterns
- Use consistent ID patterns
- Handle errors gracefully

### Performance
- Support GET requests for queries
- Implement batching to avoid N+1 queries
- Use DataLoader pattern for efficient data loading
- Enable GZIP compression
- Monitor performance metrics

**Performance Optimizations:**
- Query batching
- Response caching
- Connection pooling
- Field-level resolvers

**Recap:**
- Optimize network requests
- Implement batching
- Monitor performance

### Caching
- Use globally unique object identifiers
- Support HTTP caching for queries
- Enable client-side caching in Apollo
- Consider CDN caching for public data

**Recap:**
- Consistent object identification
- Multiple caching layers
- Cache-aware schema design

### API Communication Standards
- Accept application/json Content-Type
- Support application/graphql-response+json
- Use standard 2xx status codes for success
- Include data/errors in responses

**Standard Response Format:**
```json
{
  "data": {
    // Results here
  },
  "errors": [
    // Errors here if any
  ]
}
```

**Recap:**
- Consistent content types
- Standard response format
- Clear error handling

---

## Domain Modeling & Best Practices

### Graph-Based Domain Modeling
- Model business domain as a graph using GraphQL schema
- Define types and their relationships as nodes and edges
- Create patterns similar to Object-Oriented Programming on the client
- Support flexible backend implementations

**Example Domain Model:**
```graphql
type Appointment {
  id: ID!
  client: Client!
  service: Service!
  startTime: DateTime!
  duration: Int!
  status: AppointmentStatus!
}

type Client {
  id: ID!
  name: String!
  appointments: AppointmentConnection!
}
```

**Recap:**
- Use graph structure for intuitive modeling
- Focus on relationships between types
- Enable flexible implementations

### Schema Language & Naming
- Develop shared understanding of business domain
- Use clear, consistent naming conventions
- Choose intuitive, durable names for types and fields
- Consider query patterns when designing schema

**Naming Guidelines:**
- Use domain-specific terminology
- Keep names descriptive but concise
- Be consistent with casing and pluralization
- Think about future extensibility

**Recap:**
- Prioritize clarity and consistency
- Use domain-specific language
- Design for long-term maintainability

### Business Logic Layer
![alt text](business_layer.68bf746f-opt-640.WEBP)

- Single source of truth for business rules
- Handle validation and authorization
- Process requests consistently across endpoints
- Separate concerns between GraphQL and business logic

**Key Principles:**
- Centralized business rule enforcement
- Consistent validation across entry points
- Clear separation of concerns
- Maintainable and testable logic

**Recap:**
- Centralize business rules
- Ensure consistent processing
- Maintain clear responsibilities

### Legacy Data Integration
- Design schema for client usage patterns
- Abstract legacy data structures
- Focus on "how" rather than "what"
- Enable future implementation changes

**Best Practices:**
- Hide legacy complexity
- Provide clean abstractions
- Enable gradual modernization
- Maintain backwards compatibility

**Recap:**
- Focus on client needs
- Abstract legacy systems
- Enable future changes

---

## Success Criteria
- A fully functional booking system with seamless GraphQL integration.
- Efficient data handling and querying through Strawberry GraphQL.
- Secure authentication and role-based access control.
- Well-structured and maintainable backend with SQLAlchemy.
- Scalability for future migration to React.
