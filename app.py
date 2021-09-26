# udpate for pull request
from flask import Flask, request, render_template
import redis
import psycopg2
import json
import logging
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)

def initialize():
    global p
    global r
    try:

        postgres_host = os.getenv("POSTGRES_HOST")
        postgres_port = os.getenv("POSTGRES_PORT")

        redis_host = os.getenv("REDIS_HOST")
        redis_port = os.getenv("REDIS_PORT")

        p = psycopg2.connect(user="postgres",
                            password="postgres",
                            host=postgres_host,
                            port=postgres_port,
                            database="hello")
        r = redis.Redis(host=redis_host, port=redis_port)

    except (Exception) as e:
        logging.exception("message")
        return False
    return True

@app.route("/users", methods = ['POST', 'GET'])
def users():

    if request.method == 'GET':
        id   = request.args.get('id')
        name = request.args.get('name')

        try:
            c = p.cursor()
            if id:
                c.execute("SELECT * FROM users WHERE id = %s;", (id,))
                record = c.fetchone()
            elif name and not id:
                c.execute("SELECT * FROM users WHERE name = %s;", (name,))
                record = c.fetchmany()
            else:
                c.execute("SELECT * FROM users")
                record = c.fetchall()
        except (Exception) as e:
            c.close()
            return 'Database query failed', 503
        finally:
            keys=("id", "name", "address", "phone")
            if id:
                list_of_dict = dict(zip(keys, record))
            else:
                list_of_dict = [dict(zip(keys, values)) for values in record]
            json_out = json.dumps(list_of_dict)
            c.close()
            return json_out


    if request.method == 'POST':
        d = request.get_json()
        if not d:
            return 'JSON POST failure', 400
        else:
            name_entry  = d.get('name')
            addr_entry  = d.get('address')
            phone_entry = d.get('phone')
            if not name_entry or not addr_entry or not phone_entry:
                return 'Input error: Invalid input\n', 400

            insert_statement = 'INSERT INTO users (name, address, phone) VALUES (%s, %s, %s) RETURNING id'
            data = (name_entry, addr_entry, phone_entry)

            try:
                c = p.cursor()
                c.execute(insert_statement, data)
                id_of_new_row = c.fetchone()[0]
            except (Exception) as e:
                c.rollback()
                c.close()
                return 'Database insert failed\n', 503
            finally:
                p.commit()
                c.close()
                return 'New entry id : ' + str(id_of_new_row) + '\n'

            
@app.route("/key", methods = ['POST', 'GET'])
def key():

    if request.method == 'GET':
        key = request.args.get('key')

        logger.info('starting GET path')
        if not key:
            return 'Key must be specified\n', 400

        try:
            s = r.get(key)

            if s:
                return s.decode("utf-8") + '\n'
            else:
                return 'key not found' + '\n'

        except Exception as e:
            return 'Could not connect to cache', 503

    if request.method == 'POST':
    # curl -X POST -H "Content-Type:application/json" -d '{"key":"name", "value":"dave"}' localhost:5000/key

        logger.info('starting POST path')
        d = request.get_json()
        if not d:
            return 'JSON POST failure', 400
        else:
            key = d['key']
            value = d['value']
            if 'ttl' in d:
                ttl = d['ttl']
            else:
                ttl=None

            try:
                s = r.set(key, value, ex=ttl)

                if s:
                    return 'Key written successfully' + '\n'
                else:
                    return 'Key write failed', 400

            except Exception as e:
                return 'Could not write to cache', 503

@app.route("/hello")
def hello():

    s = str(r.get('name'))

    if not s:
        s = "World"

    return 'Hello, ' + s  + '!\n'
     
if __name__ == '__main__':
    success = initialize()
    if not success:
        print(f'Could not connect to database')
        exit(1)

    app.run(debug=True, host='0.0.0.0')

    p.close()
    r.close()
