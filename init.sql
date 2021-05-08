CREATE USER postgres;
CREATE DATABASE hello;
GRANT ALL PRIVILEGES ON DATABASE hello TO postgres;
CREATE TABLE users (id SERIAL PRIMARY KEY, name varchar, address varchar, phone varchar);
