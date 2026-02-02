CREATE TABLE IF NOT EXISTS vk (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    text TEXT,
    created_date TIMESTAMP,
    rubrics jsonb
)
