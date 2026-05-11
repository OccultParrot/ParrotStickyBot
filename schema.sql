DROP TABLE IF EXISTS sticky_messages;
CREATE TABLE sticky_messages
(
    id          SERIAL PRIMARY KEY,
    message_id  BIGINT NOT NULL UNIQUE,
    channel_id  BIGINT NOT NULL,
    guild_id    BIGINT NOT NULL,
    title       TEXT   NOT NULL,
    description TEXT   NOT NULL,
    color       TEXT
);
