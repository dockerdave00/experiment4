from flask import Flask, request, render_template
from psycopg2 import Error
import psycopg2
import json
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/users", methods = ['POST', 'GET'])
def users():

    if request.method == 'GET':
        name = request.args.get('name')
        # If both are specified, id takes precedence?

    if not name:
        record = ('','','','')
        return_string='{"id":"'      + str(record[0]) + \
                    '", "name":"'    + record[1] + \
                    '", "address":"' + record[2] + \
                    '", "phone":"'   + record[3] + '"}'
        return '\n' + return_string + '\n'

    else:

        try:
            p = psycopg2.connect(user="postgres",
                                password="postgres",
                                host="172.17.0.1",
                                port="5432",
                                database="hello")

            c = p.cursor()
            c.execute("SELECT * FROM users WHERE name = %s;", (name,))

            record = c.fetchone()
            if not record:
                record = ('','','','')

            return_string='{"id":"'      + str(record[0]) + \
                        '", "name":"'    + record[1] + \
                        '", "address":"' + record[2] + \
                        '", "phone":"'   + record[3] + '"}'
            return '\n' + return_string + '\n'
        except (Exception, Error) as error:
            return 'Could not connect to cache', 503

        c.close()
        p.close()

#@app.route("/key", methods = ['POST', 'GET'])
#def key():
#
#    if request.method == 'GET':
#        key = request.args.get('key')
#
#        logger.info('starting GET path')
#        if not key:
#            return 'Key must be specified\n', 400
#
#        try:
#            s = r.get(key)
#
#            if s:
#                return s.decode("utf-8") + '\n'
#            else:
#                return 'key not found' + '\n'
#
#        except Exception as e:
#            return 'Could not connect to cache', 503
#
#    if request.method == 'POST':
#
#        logger.info('starting POST path')
#        d = request.get_json()
#        if not d:
#            return 'JSON POST failure', 400
#        else:
#            key = d['key']
#            value = d['value']
#            if 'ttl' in d:
#                ttl = d['ttl']
#            else:
#                ttl=None
#
#            try:
#                s = r.set(key, value, ex=ttl)
#
#                if s:
#                    return 'Key written successfully' + '\n'
#                else:
#                    return 'Key write failed', 400
#
#            except Exception as e:
#                return 'Could not write to cache', 503
#
#@app.route("/hello")
#def hello():
#
#    s = str(r.get('name'))
#
#    if not s:
#        s = "World"
#
#    return 'Hello, ' + s  + '!\n'
     
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
