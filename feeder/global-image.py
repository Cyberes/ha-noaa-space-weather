import io
import logging
import pickle
import time
from datetime import datetime, timedelta

import schedule
from PIL import Image
from redis import Redis

from lib.tecmap import plot_tec_map

logging.basicConfig(level=logging.INFO)

# Entire planet
LAT_RANGE_MIN = -90
LAT_RANGE_MAX = 90
LON_RANGE_MIN = -180
LON_RANGE_MAX = 180


def get_utc_offset():
    timestamp = time.time()
    local_time = datetime.fromtimestamp(timestamp)
    utc_time = datetime.utcfromtimestamp(timestamp)
    delta = local_time - utc_time
    return delta.total_seconds() / 3600


def main():
    redis = Redis(host='localhost', port=6379, db=0)

    utc_hr = datetime.utcnow().hour
    logging.info(f'Generating plot for hour {utc_hr}')

    data = redis.get('tecmap_data')
    while data is None:
        logging.warning('Redis has not been populated yet. Is cache.py running? Sleeping 10s...')
        time.sleep(10)
        data = redis.get('tecmap_data')
    ionex_data = pickle.loads(data)

    for tecmap, epoch in ionex_data:
        if epoch.hour == utc_hr:
            plt = plot_tec_map(tecmap, [float(LON_RANGE_MIN), float(LON_RANGE_MAX)], [float(LAT_RANGE_MIN), float(LAT_RANGE_MAX)], timestamp=epoch - timedelta(hours=get_utc_offset()))[1]
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=110)
            plt.close()
            del plt

            buf.seek(0)
            img = Image.open(buf)
            buf = io.BytesIO()
            img.save(buf, format='PNG')

            redis.set('global_map', buf.getvalue())
            buf.close()
    logging.info(f'Finished hour {utc_hr}')


if __name__ == '__main__':
    main()
    schedule.every().hour.at(':00').do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
