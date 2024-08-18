import logging
from datetime import timedelta, datetime

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_URL = "https://services.swpc.noaa.gov/products/noaa-scales.json"
SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    session = async_get_clientsession(hass)
    async_add_entities([
        SpaceWeatherScaleSensor(session, CONF_URL, "R", '0', ''),
        SpaceWeatherScaleSensor(session, CONF_URL, "S", '0', ''),
        SpaceWeatherScaleSensor(session, CONF_URL, "G", '0', ''),
        SpaceWeatherScaleSensor(session, CONF_URL, "R", '-1', '_24hr'),
        SpaceWeatherScaleSensor(session, CONF_URL, "S", '-1', '_24hr'),
        SpaceWeatherScaleSensor(session, CONF_URL, "G", '-1', '_24hr'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MinorProb", "pred_r_minor"),
        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MajorProb", "pred_r_major"),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Scale", "pred_s_scale"),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Prob", "pred_s_prob"),
        SpaceWeatherPredictionSensor(session, CONF_URL, "G", "Scale", "pred_g_scale"),
        SpaceWeatherDateStampSensor(session, CONF_URL),
    ], True)


class SpaceWeatherScaleSensor(Entity):
    def __init__(self, session, url, scale_key, data_selector, trailing):
        self._session = session
        self._url = url
        self._scale_key = scale_key
        self._name = f'Space Weather Scale {scale_key} {trailing}'
        self._state = None
        self._data = None
        self._data_selector = data_selector
        self._trailing = trailing

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"space_weather_scale_{self._scale_key.lower()}{self._trailing.replace('_', '')}"

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        if self._data:
            return {
                "scale": self._data[self._scale_key]["Scale"],
                "text": self._data[self._scale_key]["Text"],
            }
        return None

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        try:
            async with self._session.get(self._url) as response:
                if response.status == 200:
                    data = await response.json()
                    self._data = data[self._data_selector]
                    self._state = f'{self._scale_key}{self._data[self._scale_key]["Scale"]}'
                else:
                    _LOGGER.error(f"Error fetching data from {self._url}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {self._url}: {err}")


class SpaceWeatherPredictionSensor(Entity):
    def __init__(self, session, url, scale_key, pred_key, unique_id):
        self._session = session
        self._url = url
        self._scale_key = scale_key
        self._pred_key = pred_key
        self._unique_id = unique_id
        self._name = f'Space Weather Prediction {scale_key} {pred_key}'
        self._state = None
        self._data = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        if self._pred_key == "Scale":
            return self._state
        elif self._state is not None:
            try:
                return float(self._state)
            except ValueError:
                return None
        return None

    @property
    def unit_of_measurement(self):
        if self._pred_key in ["MinorProb", "MajorProb", "Prob"]:
            return "%"
        return None

    @property
    def device_state_attributes(self):
        if self._data:
            return {
                "date_stamp": self._data["DateStamp"],
                "time_stamp": self._data["TimeStamp"],
            }
        return None

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        try:
            async with self._session.get(self._url) as response:
                if response.status == 200:
                    data = await response.json()
                    now = datetime.now() + timedelta(days=1)
                    tomorrow_date = now.strftime('%Y-%m-%d')
                    tomorrow_data = {}
                    for k, v in data.items():
                        datestamp = v['DateStamp']
                        if datestamp == tomorrow_date:
                            tomorrow_data = v
                    assert len(tomorrow_data.keys()) is not None
                    self._data = tomorrow_data
                    self._state = self._data[self._scale_key][self._pred_key]
                else:
                    _LOGGER.error(f"Error fetching data from {self._url}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {self._url}: {err}")


class SpaceWeatherDateStampSensor(Entity):
    """
    Attributes don't seem to be working so we use a single sensor to track the timestamp of the space weather
    prediction updated.
    """

    def __init__(self, session, url):
        self._session = session
        self._url = url
        self._name = "Space Weather Prediction Date Stamp"
        self._state = None
        self._data = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return "space_weather_prediction_date_stamp"

    @property
    def state(self):
        return self._state

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        try:
            async with self._session.get(self._url) as response:
                if response.status == 200:
                    data = await response.json()
                    now = datetime.now() + timedelta(days=1)
                    tomorrow_date = now.strftime('%Y-%m-%d')
                    tomorrow_data = {}
                    for k, v in data.items():
                        datestamp = v['DateStamp']
                        if datestamp == tomorrow_date:
                            tomorrow_data = v
                    assert len(tomorrow_data.keys()) is not None
                    self._data = tomorrow_data
                    self._state = datetime.strptime(f'{self._data["DateStamp"]}', "%Y-%m-%d").strftime('%m-%d-%Y')
                else:
                    _LOGGER.error(f"Error fetching data from {self._url}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {self._url}: {err}")
