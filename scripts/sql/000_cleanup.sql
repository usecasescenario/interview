-- Удаление дубликатов по text + created_date

DELETE FROM vk
WHERE id IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY text, created_date ORDER BY id) as row_num
        FROM vk
    ) t
    WHERE t.row_num > 1
);
