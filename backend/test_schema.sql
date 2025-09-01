-- Test script to verify the user_profiles table can be created
-- Run this in your Supabase SQL editor to test the schema

-- First, let's create a simple version to test
CREATE TABLE IF NOT EXISTS test_user_profiles (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    age INTEGER,
    email TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test insert
INSERT INTO test_user_profiles (id, full_name, age, email) 
VALUES (
    gen_random_uuid(), 
    'Test User', 
    25, 
    'test@example.com'
);

-- Test select
SELECT * FROM test_user_profiles;

-- Clean up test table
DROP TABLE test_user_profiles;

-- If the above works, you can run the full schema from database_schema.sql




