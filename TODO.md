# TODOs

## Completed
- [x] Fixed User model timestamp handling
  - Updated updated_at to use server_default
  - Added migration to ensure database consistency
  - Fixed NULL value violations

## Pending
- [ ] Add validation tests for User model timestamp behavior
- [ ] Consider adding similar timestamp handling to other models for consistency
- [ ] Add documentation for timestamp behavior in models
- [ ] Review and update GraphQL schema to reflect timestamp handling

## Future Improvements
- [ ] Consider adding created_by/updated_by tracking
- [ ] Add audit logging for important model changes
- [ ] Implement soft delete functionality
