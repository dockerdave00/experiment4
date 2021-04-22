from flask import Flask, request, render_template
import redis

app = Flask(__name__)

@app.route("/setname")
def setname():
    value = request.args.get('name')
    if not value:
        return 'Missing required input, 400\n'
    else:
        r = redis.Redis(host='172.17.0.1', port=6379)
        s = r.set('name', value, ex=30)

        if s:
            return 'Cache set successful\n'
        else:
            return 'Cache set failure\n'

@app.route("/hello")
def hello():

    r = redis.Redis(host='172.17.0.1', port=6379)
    s = str(r.get('name'))

    if not s:
        s = "World"

    return 'Hello, ' + s  + '!\n'
     
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
