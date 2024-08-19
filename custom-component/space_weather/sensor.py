import logging
from datetime import timedelta, datetime

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_URL = "https://services.swpc.noaa.gov/products/noaa-scales.json"
SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    session = async_get_clientsession(hass)
    async_add_entities([
        SpaceWeatherScaleSensor(session, CONF_URL, "R", '0', None),
        SpaceWeatherScaleSensor(session, CONF_URL, "S", '0', None),
        SpaceWeatherScaleSensor(session, CONF_URL, "G", '0', None),
        SpaceWeatherScaleSensor(session, CONF_URL, "R", '-1', '24hr_max'),
        SpaceWeatherScaleSensor(session, CONF_URL, "S", '-1', '24hr_max'),
        SpaceWeatherScaleSensor(session, CONF_URL, "G", '-1', '24hr_max'),

        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MinorProb", "1", 'today'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MajorProb", "1", 'today'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Scale", "1", 'today'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Prob", "1", 'today'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "G", "Scale", "1", 'today'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MinorProb", "2", '1day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MajorProb", "2", '1day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Scale", "2", '1day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Prob", "2", '1day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "G", "Scale", "2", '1day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MinorProb", "3", '2day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "R", "MajorProb", "3", '2day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Scale", "3", '2day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "S", "Prob", "3", '2day'),
        SpaceWeatherPredictionSensor(session, CONF_URL, "G", "Scale", "3", '2day'),
    ], True)


class SpaceWeatherScaleSensor(Entity):
    def __init__(self, session, url, scale_key, data_selector, trailing):
        self._session = session
        self._url = url
        self._scale_key = scale_key

        self._name = f'Space Weather Scale {scale_key}'
        if trailing is not None and len(trailing):
            self._name = self._name + ' ' + trailing.replace("_", " ").replace("  ", " ")

        self._data = None
        assert isinstance(data_selector, str)
        self._data_selector = data_selector
        self._trailing = trailing

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        s = f"space_weather_scale_{self._scale_key.lower()}"
        if self._trailing is not None and len(self._trailing):
            s = s + '_' + self._trailing.strip('_')
        return s

    @property
    def state(self):
        return f'{self._scale_key}{self._data[self._scale_key]["Scale"]}'

    @property
    def extra_state_attributes(self):
        if self._data:
            return {
                "scale_int": int(self._data[self._scale_key]["Scale"]),
                "text": self._data[self._scale_key]["Text"],
                "timestamp": datetime.fromisoformat(self._data["DateStamp"] + 'T' + self._data["TimeStamp"] + '+00:00').isoformat()
            }
        return None

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        try:
            async with self._session.get(self._url) as response:
                if response.status == 200:
                    data = await response.json()
                    self._data = data[self._data_selector]
                else:
                    _LOGGER.error(f"Error fetching data from {self._url}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {self._url}: {err}")


class SpaceWeatherPredictionSensor(Entity):
    def __init__(self, session, url, scale_key, pred_key, data_selector, trailing):
        self._session = session
        self._url = url
        self._scale_key = scale_key
        self._pred_key = pred_key
        self._data_selector = data_selector
        self._trailing = trailing
        self._name = f'Space Weather Prediction {scale_key} {pred_key} {trailing.replace("_", " ").replace("  ", " ")}'
        self._state = None
        self._data = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f'space_weather_pred_{self._scale_key}_{self._pred_key}_{self._trailing}'.lower()

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
    def extra_state_attributes(self):
        if self._data:
            return {
                "timestamp": datetime.fromisoformat(self._data["DateStamp"] + 'T' + self._data["TimeStamp"] + '+00:00').isoformat()
            }
        return None

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        try:
            async with self._session.get(self._url) as response:
                if response.status == 200:
                    data = await response.json()
                    self._data = data[self._data_selector]
                    self._state = self._data[self._scale_key][self._pred_key]
                else:
                    _LOGGER.error(f"Error fetching data from {self._url}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {self._url}: {err}")
