DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'outbox_status') THEN
        CREATE TYPE outbox_status AS ENUM ('pending', 'processed', 'failed');
    END IF;
END
$$;
CREATE TABLE IF NOT EXISTS outbox (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payload       JSONB NOT NULL,
    status        outbox_status DEFAULT 'pending',
    retries       INTEGER DEFAULT 0,
    created_at    TIMESTAMP DEFAULT NOW(),
    processed_at  TIMESTAMP ,
    error_message TEXT
);

-- Индекс для worker.py, чтобы тот мог быстро находить необработаннные строки
CREATE INDEX IF NOT EXISTS idx_outbox_status_pending
ON outbox (created_at) 
WHERE status = 'pending';
