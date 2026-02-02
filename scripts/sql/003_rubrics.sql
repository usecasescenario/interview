INSERT INTO vk (text, created_date, rubrics)
SELECT
    text,
    created_date::timestamp,
    replace(rubrics_raw, '''', '"')::jsonb
FROM vk_staging
ON CONFLICT DO NOTHING; -- На случай, если эта строка уже есть в vk
