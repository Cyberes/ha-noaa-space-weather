import io
import logging
import pickle
import sys
from datetime import datetime
from typing import List

from PIL import Image
from redis import Redis

from lib.tecmap import plot_tec_map

logging.basicConfig(level=logging.INFO)

LAT_RANGE_MIN = -90
LAT_RANGE_MAX = 90
LON_RANGE_MIN = -180
LON_RANGE_MAX = 180

redis = Redis(host='localhost', port=6379, db=0)

utc_hr = datetime.utcnow().hour
logging.info(f'Generating plot for hour {utc_hr}')

ionex_data: List = pickle.loads(redis.get('tecmap_data'))
if ionex_data is None:
    logging.critical('Redis has not been populated yet. Is cache.py running?')
    sys.exit(1)

for tecmap, epoch in ionex_data:
    if epoch.hour == utc_hr:
        plt = plot_tec_map(tecmap, [float(LON_RANGE_MIN), float(LON_RANGE_MAX)], [float(LAT_RANGE_MIN), float(LAT_RANGE_MAX)])[1]

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=110)
        plt.close()
        del plt

        buf.seek(0)
        img = Image.open(buf)
        # img = img.resize((img.size[0], 500), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='PNG')

        redis.set('global_map', buf.getvalue())
        buf.close()
