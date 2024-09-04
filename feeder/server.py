import datetime
import io

import redis
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file, make_response

NO_MAP_STR = 'NO GLOBAL MAP AVAILABLE'

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379)


@app.route('/global')
def serve_global_map():
    global_map_data = redis_client.get('global_map')
    if global_map_data is None:
        img = Image.new('RGB', (500, 300), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        fnt = ImageFont.load_default(size=30)
        w, h = fnt.getbbox(NO_MAP_STR)[2:4]
        d.text(((500 - w) / 2, (300 - h) / 2), NO_MAP_STR, font=fnt, fill=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

    buf = io.BytesIO(global_map_data)
    buf.seek(0)
    response = make_response(send_file(buf, mimetype='image/png'))
    expires = datetime.datetime.now()
    expires = expires + datetime.timedelta(minutes=10)
    response.headers['Cache-Control'] = 'public, max-age=600'
    response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return response


if __name__ == '__main__':
    app.run()
