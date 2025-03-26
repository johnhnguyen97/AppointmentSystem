# Appointment System Backend Tests

## Test Setup

1. Make sure you have Python 3.12+ installed
2. Run the test runner script:
   ```bash
   python run_tests.py
   ```
   The script will automatically:
   - Create/activate virtual environment if needed
   - Install required dependencies
   - Set up test directories
   - Run tests and generate reports

## Running Tests

You can run tests in several ways:

```bash
# Run all tests
python run_tests.py

# Run tests with specific marker
python run_tests.py -m integration
python run_tests.py -m database

# Run tests matching a pattern
python run_tests.py -k "test_admin"

# Run with custom pytest arguments
python run_tests.py -v -s --pdb
```

The test runner will:
- Automatically activate/create the virtual environment
- Run tests with proper configuration
- Generate an HTML report in `test-reports/{timestamp}/report.html`
- Show a summary of test results
- Open the HTML report in your browser

## Test Structure

- `src/tests/` - Main test directory
  - `conftest.py` - Test fixtures and database setup
  - `test_auth.py` - Authentication tests
  - `test_db_connection.py` - Database connection tests

## Test Reports

Test reports are generated in timestamped directories under `test-reports/`. Each report includes:

- Test results with pass/fail status
- Test duration and timing information
- Test environment details
- Error messages and tracebacks for failed tests
- Custom styling and formatting

## Available Test Markers and Options

The test runner supports all standard pytest arguments and these markers:

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.database` - Database-dependent tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.slow` - Long-running tests

## Troubleshooting

1. If you get database connection errors:
   - Verify PostgreSQL is running
   - Check your .env file has correct database settings

2. If tests hang:
   - Check if previous test runs left hanging connections
   - Restart PostgreSQL service

3. If HTML report is not generated:
   - Ensure you have write permissions in the test-reports directory
   - Try running the setup script again
