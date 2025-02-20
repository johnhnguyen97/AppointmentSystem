-- Check the actual enum values
SELECT t.typname, e.enumlabel
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'service_type'
ORDER BY e.enumsortorder;
