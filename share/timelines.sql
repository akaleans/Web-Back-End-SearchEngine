-- $ sqlite3 timelines.db < timelines.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS timelines;
CREATE TABLE timelines (
	id INTEGER primary key,
	username VARCHAR,
	text VARCHAR,
	time INTEGER
);
INSERT INTO timelines(username, text, time) VALUES('kstensby', 'Hello, this is my first post HAHAHEHEHUHU', CURRENT_TIMESTAMP);
INSERT INTO timelines(username, text, time) VALUES('rwalls', 'Hello, mesodumb', CURRENT_TIMESTAMP);
INSERT INTO timelines(username, text, time) VALUES('zjeffries', 'Hello, my name is Zook', CURRENT_TIMESTAMP);
COMMIT;
