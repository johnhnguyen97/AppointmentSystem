# Appointment System Testing Guide

## Overview
This directory contains various testing tools for the appointment system, focusing on client creation, appointment booking flows, and GraphQL functionality.

## Test Structure

### 1. GraphQL Tests

#### Basic GraphQL Tests (`test_graphql.py`)
- User authentication and token management
- Basic CRUD operations for appointments
- Query and mutation fundamentals
- Simple appointment creation and retrieval

#### Advanced GraphQL Tests (`test_graphql_advanced.py`)
- Appointment overlap prevention
- Status transition validation
- Service history tracking
- Enhanced authorization and role-based access
- Complex mutation validations

### 2. Client Flow Tests

#### Interactive Testing (`test_client_flow.py`)
```bash
# Run the interactive test script
python src/test/test_client_flow.py
```
- Complete client workflow testing
- Individual component testing
- Error case validation
- Appointment viewing

#### Unit Tests (`test_client_appointments.py`)
```bash
# Run unit tests with coverage
pytest --cov=src/main src/test/
```
- Client creation validation
- Appointment scheduling rules
- Time constraint checks
- Service type validation

## Test Categories

### Validation Tests
- Appointment time constraints
- Service type validation
- Status transition rules
- Authorization checks
- Overlap prevention

### Integration Tests
- Client-Provider interactions
- Service history tracking
- Appointment scheduling flow
- GraphQL mutation chains

### Authorization Tests
- Role-based access control
- Admin vs provider permissions
- Client self-service restrictions
- Token validation

## Running Tests

### Method 1: Using pytest
```bash
# Run all tests
pytest

# Run specific test file
pytest src/test/test_graphql_advanced.py

# Run with verbose output
pytest -v src/test/test_graphql_advanced.py

# Run with coverage report
pytest --cov=src/main --cov-report=term-missing
```

### Method 2: Using GraphQL Playground
1. Open GraphQL playground at http://localhost:8000/graphql
2. Follow steps in client_self_service_flow.md
3. Execute test queries from graphql_test_queries.md
4. Verify responses match expected results

## Common Issues and Solutions

### 1. Authorization Errors
```json
{
  "errors": [
    {
      "message": "Not authenticated"
    }
  ]
}
```
Solution: Ensure auth token is included in headers

### 2. Appointment Overlap Error
```json
{
  "errors": [
    {
      "message": "Appointment overlaps with existing booking"
    }
  ]
}
```
Solution: Check existing appointments and choose non-conflicting time

### 3. Invalid Status Transition
```json
{
  "errors": [
    {
      "message": "Invalid status transition"
    }
  ]
}
```
Solution: Follow valid status transition paths (SCHEDULED -> CONFIRMED -> COMPLETED)

## Future Improvements

### 1. Test Coverage
- Add more edge cases for overlap detection
- Enhance authorization test scenarios
- Add performance testing

### 2. Integration Testing
- Add end-to-end flow tests
- Test external service integrations
- Add load testing scenarios

### 3. Documentation
- Add more test case examples
- Document common failure scenarios
- Include performance benchmarks
