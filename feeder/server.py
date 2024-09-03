import io

import redis
from flask import Flask, send_file

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379)


@app.route('/global')
def serve_global_map():
    global_map_data = redis_client.get('global_map')
    if global_map_data is None:
        return "No global map available", 400

    buf = io.BytesIO(global_map_data)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


if __name__ == '__main__':
    app.run()
