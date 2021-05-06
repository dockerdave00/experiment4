from flask import Flask, request, render_template
import redis
import psycopg2
from psycopg2.extensions import AsIs
import json
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

def initialize():
    global p
    global r
    try:
        p = psycopg2.connect(user="postgres",
                            password="postgres",
                            host="172.17.0.1",
                            port="5432",
                            database="hello")

        r = redis.Redis(host='172.17.0.1', port=6379)
    except (Exception) as e:
        return False
    return True

@app.route("/users", methods = ['POST', 'GET'])
def users():

    # If both are specified, id takes precedence
    if request.method == 'GET':

        c = p.cursor()

        id   = request.args.get('id')
        name = request.args.get('name')

        try:
            if id:
                c.execute("SELECT * FROM users WHERE id = %s;", (id,))
                record = c.fetchmany()
            elif name and not id:
                c.execute("SELECT * FROM users WHERE name = %s;", (name,))
                record = c.fetchmany()
            elif not id and not name:
                c.execute("SELECT * FROM users")
                record = c.fetchall()
        except (Exception) as e:
            return 'Could not connect to database', 503
            exit(1)

        if not record:
            return_string = ""
        else:
            return_string = ""
            for entry in record:
                entry_string='{"id":"'      + str(entry[0]) + \
                           '", "name":"'    + entry[1] + \
                           '", "address":"' + entry[2] + \
                           '", "phone":"'   + entry[3] + '"}'
                return_string += entry_string + '\n'

        return '\n' + return_string + '\n'
        c.close()

    if request.method == 'POST':
        e = ""
        # curl -X POST -H "Content-Type:application/json" -d '{"name":"Chris", "address":"2345 DNA Dumpster Lane", "phone":"123-456-7890"}' localhost:5000/users
        d = request.get_json()
        if not d:
            return 'JSON POST failure', 400
        else:
            columns = d.keys()
            values = [d[column] for column in columns]
            insert_statement = 'INSERT INTO users (%s) VALUES %s RETURNING id'

            try:
                c = p.cursor()
                c.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
                id_of_new_row = c.fetchone()[0]
            except (Exception) as e:
                print(f"error = {e}" )
                return 'Could not connect to database', 503
            
        if not e:
            return str(id_of_new_row) + '\n'
        else:
            return '\n END FUNCTION \n'

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
        print(f'Could not connect to services, HTTP: 503')
        exit(1)
    app.run(debug=True, host='0.0.0.0')
