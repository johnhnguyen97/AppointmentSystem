/*
 * Database permissions script for test environment
 *
 * This script should be run by a PostgreSQL superuser or a user with GRANT permissions
 * Usage: psql -f grant_test_permissions.sql -v test_db_user="$(echo $TEST_DB_USER)"
 */

-- Grant permissions to the test user (variable comes from environment)
GRANT CONNECT ON DATABASE :test_db ON ROLE :"test_db_user";
GRANT USAGE ON SCHEMA public TO :"test_db_user";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO :"test_db_user";
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public TO :"test_db_user";

-- If you need write access for some tests:
-- GRANT INSERT, UPDATE, DELETE ON public.users TO :"test_db_user";
-- GRANT INSERT, UPDATE, DELETE ON [other_tables] TO :"test_db_user";

-- Grant specific permissions for test scenarios
GRANT SELECT ON public.users TO :"test_db_user";
