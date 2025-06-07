-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Optional: Create a test table using vector
-- DROP TABLE IF EXISTS documents;
-- CREATE TABLE documents (
--   id serial PRIMARY KEY,
--   content text,
--   embedding vector(1536)  -- replace 1536 with your embedding size
-- );
