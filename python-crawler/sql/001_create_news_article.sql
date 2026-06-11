CREATE TABLE IF NOT EXISTS news_article (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source VARCHAR(100) NOT NULL,
    published_at TIMESTAMPTZ,
    content_summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_article_published_at
    ON news_article (published_at DESC);

CREATE INDEX IF NOT EXISTS idx_news_article_source
    ON news_article (source);
