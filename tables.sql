CREATE TABLE blacklist(
     snowflake_id BIGINT PRIMARY KEY,
     REASON VARCHAR(4000),
     timestamp TIMESTAMP);

CREATE TABLE commands_list(
     guild_id BIGINT NOT NULL,
     bot_id BIGINT NOT NULL,
     command VARCHAR(100) NOT NULL,
     time_used TIMESTAMP);

CREATE TABLE prefixes_list(
     guild_id BIGINT NOT NULL,
     bot_id BIGINT NOT NULL,
     prefix VARCHAR(100),
     usage INTEGER NOT NULL,
     last_usage TIMESTAMP NOT NULL,
     UNIQUE(guild_id, bot_id, prefix));

CREATE TABLE bot_repo(
     bot_id BIGINT NOT NULL,
     owner_repo VARCHAR(2000),
     bot_name VARCHAR(2000),
     certainty NUMERIC(20, 2),
     PRIMARY KEY(bot_id));

CREATE TABLE confirmed_bots(
     bot_id BIGINT,
     author_id BIGINT,
     reason VARCHAR(2000),
     requested_at TIMESTAMP,
     jump_url VARCHAR(1000),
     joined_at TIMESTAMP,
     UNIQUE(bot_id)
);

CREATE TABLE pending_bots(
     bot_id BIGINT PRIMARY KEY,
     author_id BIGINT,
     reason VARCHAR(2050),
     requested_at TIMESTAMP,
     jump_url VARCHAR(1000)
);

CREATE TABLE reports(
     report_id SERIAL,
     user_id BIGINT NOT NULL,
     finish BOOLEAN NOT NULL,
     reported_at TIMESTAMP,
     PRIMARY KEY (report_id)
);

CREATE TABLE resport_respond(
     report_id BIGINT NOT NULL,
     user_id BIGINT NOT NULL,
     interface_id BIGINT,
     message_id BIGINT NOT NULL,
     message VARCHAR(4000),
     FOREIGN KEY (report_id) REFERENCES reports(report_id)
);

CREATE TABLE position_letter(
     bot_id BIGINT,
     letter CHAR,
     position INT,
     count INT,
     PRIMARY KEY(bot_id, letter, "position")
);

CREATE TABLE internal_prefix(
     snowflake_id BIGINT UNIQUE,
     prefix VARCHAR(30)
);

CREATE TABLE bot_tasks(
     task_id SERIAL PRIMARY KEY,
     last_execution TIMESTAMP WITH TIME ZONE,
     next_execution TIMESTAMP WITH TIME ZONE
);