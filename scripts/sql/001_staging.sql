CREATE TABLE IF NOT EXISTS vk_staging (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    text TEXT,
    created_date TIMESTAMP,
    rubrics_raw TEXT
);
