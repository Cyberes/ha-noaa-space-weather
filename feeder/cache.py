import logging
import os
import pickle
import sys
import time
from datetime import datetime

from redis import Redis

from lib.cddis_fetch import fetch_latest_ionex
from lib.tecmap import get_tecmaps, parse_ionex_datetime

logging.basicConfig(level=logging.INFO)

CDDIS_USERNAME = os.getenv('CDDIS_USERNAME')
CDDIS_PASSWORD = os.getenv('CDDIS_PASSWORD')
if not CDDIS_USERNAME or not CDDIS_PASSWORD:
    logging.critical('Must set CDDIS_USERNAME and CDDIS_PASSWORD environment variables')
    sys.exit(1)


def main():
    redis = Redis(host='localhost', port=6379, db=0)
    redis.flushall()
    while True:
        utc_hr = datetime.utcnow().hour
        logging.info('Fetching latest IONEX data')
        logging.info(f'Using hour {utc_hr}')
        ionex_data = fetch_latest_ionex(CDDIS_USERNAME, CDDIS_PASSWORD)
        parsed_data = []
        for tecmap, epoch in get_tecmaps(ionex_data):
            parsed_dt = parse_ionex_datetime(epoch)
            parsed_data.append((tecmap, parsed_dt))
        redis.set('tecmap_data', pickle.dumps(parsed_data))
        logging.info('Scrape complete')
        time.sleep(1800)  # 30 minutes


if __name__ == '__main__':
    main()
