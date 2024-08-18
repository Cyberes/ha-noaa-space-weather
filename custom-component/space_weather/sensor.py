import logging
from datetime import timedelta

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_URL = "https://services.swpc.noaa.gov/products/noaa-scales.json"
SCAN_INTERVAL = timedelta(minutes=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional("url", default=CONF_URL): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    url = config.get("url")
    session = async_get_clientsession(hass)
    async_add_entities([
        SpaceWeatherScaleSensor(session, url, "R"),
        SpaceWeatherScaleSensor(session, url, "S"),
        SpaceWeatherScaleSensor(session, url, "G"),
        SpaceWeatherPredictionSensor(session, url, "R", "MinorProb", "pred_r_minor"),
        SpaceWeatherPredictionSensor(session, url, "R", "MajorProb", "pred_r_major"),
        SpaceWeatherPredictionSensor(session, url, "S", "Scale", "pred_s_scale"),
        SpaceWeatherPredictionSensor(session, url, "S", "Prob", "pred_s_prob"),
        SpaceWeatherPredictionSensor(session, url, "G", "Scale", "pred_g_scale"),
    ], True)


class SpaceWeatherScaleSensor(Entity):
    def __init__(self, session, url, scale_key):
        self._session = session
        self._url = url
        self._scale_key = scale_key
        self._name = f'Space Weather Scale {scale_key}'
        self._state = None
        self._data = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"space_weather_scale_{self._scale_key.lower()}"

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
                    self._data = data["-1"]
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
                    self._data = data["1"]
                    self._state = self._data[self._scale_key][self._pred_key]
                else:
                    _LOGGER.error(f"Error fetching data from {self._url}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {self._url}: {err}")
