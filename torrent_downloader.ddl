CREATE DATABASE torrent_downloader;

CREATE TABLE torrent_downloader.torrent (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    info_hash VARCHAR(64) NOT NULL UNIQUE,
    magnet_link TEXT NULL UNIQUE,
    file TEXT NULL UNIQUE,
    added_on TIMESTAMP WITH TIMEZONE,
    is_task_sent BOOLEAN DEFAULT FALSE,
    is_task_failed BOOLEAN DEFAULT FALSE,
    task_sent_on TIMESTAMP WITH TIMEZONE NULL,
    is_processing BOOLEAN DEFAULT FALSE,
    is_bad BOOLEAN DEFAULT FALSE,
    size INT NULL,

);

CREATE TABLE  torrent_downloader.user (
    id SERIAL PRIMARY KEY,
    tg_id INTEGER NULL,
    is_subscriber BOOLEAN DEFAULT FALSE,
);
