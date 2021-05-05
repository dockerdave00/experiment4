#!/bin/bash

#set -x

# Simplify commands with single word
STOP="docker stop"
CONT="docker container rm"
RUN="docker run"
EXEC="docker exec"

echo "Check if postgres container is running"
postgres_container_id=$(docker ps -a | grep postgres_db | awk '{print $1}')

if [ "${postgres_container_id}" ]; then

	echo "Stopping postgres container"
	result1=$(${STOP} postgres_db)
	if [ ${result1} != "postgres_db" ]; then
		echo -e "\tContainer stop failed"
		exit 1
	fi
	sleep 1 

	if [ "${postgres_container_id}" ]; then
		echo "Removing container"
		result2=$(${CONT} ${postgres_container_id})
		if [ ${result2} != ${postgres_container_id} ]; then
			echo -e "\tContainer remove failed"
			exit 1
		fi
	fi

fi
sleep 1 

echo "Starting postgres database container"
result3=$(${RUN} --name postgres_db -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgres:13.2)
if [ ! "${result3}" ]; then
	echo -e "\tDatabase container not created"
	exit 1
fi
sleep 1 # give docker/psql time to complete

echo "Creating 'hello' database"
result4=$(${EXEC} -it postgres_db psql --username postgres -a -c 'CREATE DATABASE hello;')
# modify command result output down to simple, usable string
result4_mod=$(echo ${result4} | tr '\r\n' ' ' | awk -F\; '{print $2}' | xargs)
if [ "${result4_mod}" != "CREATE DATABASE" ]; then
	echo -e "\t'hello' database not created"
	exit 1
fi
sleep 1 # give docker/psql time to complete

echo "Creating 'users' table in 'hello' database"
result5=$(${EXEC} -it postgres_db psql --username postgres -d hello -a -c \
	'CREATE TABLE users (id SERIAL PRIMARY KEY, name varchar, address varchar, phone varchar);')
# modify command result output down to simple, usable string
result5_mod=$(echo ${result5} | tr '\r\n' ' ' | awk -F\; '{print $2}' | xargs)
if [ "${result5_mod}" != "CREATE TABLE" ]; then
	echo -e "\t'users' table not created in 'hello' database"
	exit 1 
fi
sleep 1 # give docker/psql time to complete

echo "Populating a row of 'users' table in 'hello' database"
result6=$(${EXEC} -it postgres_db psql --username postgres -d hello -a -c \
	"INSERT INTO users(name, address, phone) VALUES ('Teresa', '8745 W Geddes Place', '303-594-9683');")
# modify command result output down to simple, usable string
result6_mod=$(echo ${result6} | tr '\r\n' ' ' | awk -F\; '{print $2}' | xargs)
if [ "${result6_mod}" == "INSERT 0 1" ]; then
	echo -e "\t** Value store successful **"
else
	echo -e "\tValue store failure"
	exit 1
fi

echo "Populating next row of 'users' table in 'hello' database"
result7=$(${EXEC} -it postgres_db psql --username postgres -d hello -a -c \
	"INSERT INTO users(name, address, phone) VALUES ('Dave', '8745 W Geddes Place', '303-204-6735');")
# modify command result output down to simple, usable string
result7_mod=$(echo ${result7} | tr '\r\n' ' ' | awk -F\; '{print $2}' | xargs)
if [ "${result7_mod}" == "INSERT 0 1" ]; then
	echo -e "\t** Value store successful **"
else
	echo -e "\tValue store failure"
	exit 1
fi

echo -e "\nDisplaying contents of 'hello' database, 'users' table\n"
${EXEC} -it postgres_db psql --username postgres -d hello -a -c "SELECT * FROM users;"

exit