CREATE DATABASE hello;
CREATE TABLE users (id SERIAL PRIMARY KEY, name varchar, address varchar, phone varchar);
INSERT INTO users (name, address, phone) VALUES ('Teresa', '8745 W Geddes Place', '303-594-9683');
INSERT INTO users (name, address, phone) VALUES ('Dave', '8745 W Geddes Place', '303-204-6735');
SELECT * FROM users;
