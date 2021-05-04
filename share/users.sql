-- $ sqlite3 users.db < users.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
	id INTEGER primary key,
	username VARCHAR,
	email VARCHAR,
	password VARCHAR,
	UNIQUE(username, email)
);
INSERT INTO users(username, email, password) VALUES('kstensby','kstensby@gmail.com','abc123');
INSERT INTO users(username, email, password) VALUES('rwalls','rwalls@gmail.com','bcd234');
INSERT INTO users(username, email, password) VALUES('zjeffries','zjeffries@gmail.com','cde345');
DROP TABLE IF EXISTS follows;
CREATE TABLE follows (
	id INTEGER primary key,
	username VARCHAR,
	follows VARCHAR
);
INSERT INTO follows(username, follows) VALUES('kstensby','rwalls');
INSERT INTO follows(username, follows) VALUES('kstensby','zjeffries');
INSERT INTO follows(username, follows) VALUES('rwalls','zjeffries');
INSERT INTO follows(username, follows) VALUES('zjeffries','kstensby');
COMMIT;
