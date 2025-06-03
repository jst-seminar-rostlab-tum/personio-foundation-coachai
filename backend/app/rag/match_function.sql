CREATE OR REPLACE FUNCTION match_documents (
    query_embedding vector(768),
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    content text,
    metadata jsonb,
    embedding vector
)
LANGUAGE sql STABLE
AS $$
    SELECT
        id,
        content,
        metadata,
        embedding
    FROM hr_information
    ORDER BY embedding <#> query_embedding
    LIMIT match_count;
$$;
