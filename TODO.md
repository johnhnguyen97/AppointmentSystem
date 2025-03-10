# TODO Items

## Test Framework Cleanup

### pytest-asyncio Warnings
- [ ] Remove `asyncio_fixture_scope` from pytest.ini once new version of pytest-asyncio is released
- [ ] Update event_loop fixture in conftest.py to use `loop_scope` argument instead of redefining the fixture
- [ ] Ensure proper event loop cleanup in tests by:
  1. Properly closing loop in event_loop fixture after yielding
  2. Avoiding overlapping event_loop fixture scopes
  3. Not modifying event loop in async fixtures or tests

## Code Improvements
- [ ] Add validation for service types in Client model
- [ ] Add constraints for appointment duration and scheduling
- [ ] Implement proper error handling for cascading deletes
- [ ] Add indexes for frequently queried columns
