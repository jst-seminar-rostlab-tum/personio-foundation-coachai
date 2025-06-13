CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector,
  match_count integer DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  embedding vector
)
AS $$
BEGIN
  RETURN QUERY
  SELECT
    hr.id,
    hr.content::text,
    hr.metadata,
    hr.embedding
  FROM hr_information AS hr
  ORDER BY hr.embedding <-> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
