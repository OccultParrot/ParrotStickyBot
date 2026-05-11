CREATE TABLE sticky_messages (
    id         SERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL UNIQUE,
    channel_id BIGINT NOT NULL,
    guild_id   BIGINT NOT NULL,
    content    TEXT   NOT NULL
);
