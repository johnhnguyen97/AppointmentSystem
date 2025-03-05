# TODO Items

## GraphQL API Improvements
- [x] Set up GraphQL console (GraphiQL) for API exploration
- [x] Create documentation for using the GraphQL console
- [x] Create script to start the GraphQL server and open the console
- [x] Create example script for programmatic GraphQL API access
- [x] Implement client appointment creation mutation
- [x] Create documentation for client appointment creation
- [x] Create test script for client appointment creation
- [ ] Add GraphQL subscriptions for real-time updates
- [ ] Implement rate limiting for GraphQL queries
- [ ] Add query complexity analysis to prevent resource-intensive queries
- [ ] Create a custom GraphQL playground theme
- [ ] Add examples for batch operations
- [ ] Implement pagination for large result sets
- [ ] Add field-level permissions based on user roles
- [ ] Create GraphQL API integration tests
- [ ] Add performance monitoring for GraphQL queries
- [ ] Implement caching for frequently used queries

## Test Framework Cleanup

### pytest-asyncio Warnings
- [ ] Remove `asyncio_fixture_scope` from pytest.ini once new version of pytest-asyncio is released
- [ ] Update event_loop fixture in conftest.py to use `loop_scope` argument instead of redefining the fixture
- [ ] Ensure proper event loop cleanup in tests by:
  1. Properly closing loop in event_loop fixture after yielding
  2. Avoiding overlapping event_loop fixture scopes
  3. Not modifying event loop in async fixtures or tests

## Client Appointment Features
- [x] Enable clients to create their own appointments
- [ ] Add support for recurring appointments
- [ ] Implement appointment reminders
- [ ] Add ability for clients to view their appointment history
- [ ] Enable clients to reschedule appointments
- [ ] Add support for service package usage when booking appointments
- [ ] Implement appointment confirmation workflow
- [ ] Add email notifications for appointment status changes
- [ ] Create client dashboard for appointment management
- [ ] Add calendar integration (iCal, Google Calendar)
- [ ] Implement appointment availability checking

## Code Improvements
- [ ] Add validation for service types in Client model
- [x] Add constraints for appointment duration and scheduling
- [ ] Implement proper error handling for cascading deletes
- [ ] Add indexes for frequently queried columns
- [ ] Create initial database migration scripts
- [ ] Set up database schema versioning

## Database Management
- [x] Install DBeaver for database management
- [x] Create setup script for DBeaver connection profiles
- [x] Create database reset script to drop and recreate tables
- [x] Create schema verification script to ensure GraphQL and database schemas are in sync
- [x] Create main database setup script that combines reset and verification
- [x] Document database management scripts
- [x] Create test data generation script with nanoid values
- [x] Create SQL script for populating database with test data
- [x] Document GraphQL queries and mutations for test data
- [ ] Create database connection profiles for development, testing, and production
- [ ] Generate ER diagram for database documentation
- [ ] Create saved queries for common database operations
- [ ] Document common SQL queries for the appointment system

## Bitwarden Integration
- [x] Create utility functions for retrieving credentials from Bitwarden
- [x] Update config.py to use Bitwarden for configuration values
- [x] Update models.py to use configuration values from settings
- [x] Create documentation for Bitwarden integration
- [x] Implement hidden password input for Bitwarden master password
- [x] Create secure password input module with masked characters (asterisks)
- [x] Document password security improvements
- [ ] Add Bitwarden integration tests
- [ ] Create script to set up initial Bitwarden vault items
- [ ] Add CI/CD pipeline support for Bitwarden
