import datetime
import io

import redis
from flask import Flask, send_file, make_response

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379)


@app.route('/global')
def serve_global_map():
    global_map_data = redis_client.get('global_map')
    if global_map_data is None:
        return "No global map available", 400

    buf = io.BytesIO(global_map_data)
    buf.seek(0)
    response = make_response(send_file(buf, mimetype='image/png'))
    expires = datetime.datetime.now()
    expires = expires + datetime.timedelta(minutes=10)
    response.headers['Cache-Control'] = 'public'
    response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return response


if __name__ == '__main__':
    app.run()
