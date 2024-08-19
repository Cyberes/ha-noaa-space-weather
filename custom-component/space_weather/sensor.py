import logging
from datetime import timedelta, datetime

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

SCALES_URL = "https://services.swpc.noaa.gov/products/noaa-scales.json"
SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    session = async_get_clientsession(hass)
    async_add_entities([
        SpaceWeatherScaleSensor(session, "R", '0', None),
        SpaceWeatherScaleSensor(session, "S", '0', None),
        SpaceWeatherScaleSensor(session, "G", '0', None),
        SpaceWeatherScaleSensor(session, "R", '-1', '24hr_max'),
        SpaceWeatherScaleSensor(session, "S", '-1', '24hr_max'),
        SpaceWeatherScaleSensor(session, "G", '-1', '24hr_max'),

        SpaceWeatherPredictionSensor(session, "R", "MinorProb", "1", 'today'),
        SpaceWeatherPredictionSensor(session, "R", "MajorProb", "1", 'today'),
        SpaceWeatherPredictionSensor(session, "S", "Scale", "1", 'today'),
        SpaceWeatherPredictionSensor(session, "S", "Prob", "1", 'today'),
        SpaceWeatherPredictionSensor(session, "G", "Scale", "1", 'today'),
        SpaceWeatherPredictionSensor(session, "R", "MinorProb", "2", '1day'),
        SpaceWeatherPredictionSensor(session, "R", "MajorProb", "2", '1day'),
        SpaceWeatherPredictionSensor(session, "S", "Scale", "2", '1day'),
        SpaceWeatherPredictionSensor(session, "S", "Prob", "2", '1day'),
        SpaceWeatherPredictionSensor(session, "G", "Scale", "2", '1day'),
        SpaceWeatherPredictionSensor(session, "R", "MinorProb", "3", '2day'),
        SpaceWeatherPredictionSensor(session, "R", "MajorProb", "3", '2day'),
        SpaceWeatherPredictionSensor(session, "S", "Scale", "3", '2day'),
        SpaceWeatherPredictionSensor(session, "S", "Prob", "3", '2day'),
        SpaceWeatherPredictionSensor(session, "G", "Scale", "3", '2day'),

        PlanetaryKIndexSensor(session)
    ], True)


class SpaceWeatherScaleSensor(Entity):
    def __init__(self, session, scale_key, data_selector, trailing):
        self._session = session
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
            async with self._session.get(SCALES_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    self._data = data[self._data_selector]
                else:
                    _LOGGER.error(f"Error fetching data from {SCALES_URL}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {SCALES_URL}: {err}")


class SpaceWeatherPredictionSensor(Entity):
    def __init__(self, session, scale_key, pred_key, data_selector, trailing):
        self._session = session
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
            async with self._session.get(SCALES_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    self._data = data[self._data_selector]
                    self._state = self._data[self._scale_key][self._pred_key]
                else:
                    _LOGGER.error(f"Error fetching data from {SCALES_URL}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {SCALES_URL}: {err}")


class PlanetaryKIndexSensor(Entity):
    """
    Temporary sensor until https://github.com/tcarwash/home-assistant_noaa-space-weather gets their shit together
    """

    def __init__(self, session):
        self._session = session
        self._name = 'Space Weather Planetary K-Index'
        self._data = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return 'space_weather_planetary_k_index'

    @property
    def state(self):
        if self._data:
            return float(self._data['kp_index'])
        return None

    # @property
    # def device_class(self):
    #     return None

    @property
    def extra_state_attributes(self):
        if self._data:
            return {
                "kp_index": float(self._data['kp_index']),
                "estimated_kp": float(self._data['estimated_kp']),
                "timestamp": datetime.fromisoformat(self._data['time_tag']).isoformat(),
                'state_class': "measurement"
            }
        return None

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        try:
            async with self._session.get('https://services.swpc.noaa.gov/json/planetary_k_index_1m.json') as response:
                if response.status == 200:
                    data = await response.json()
                    self._data = data[-1]
                else:
                    _LOGGER.error(f"Error fetching data from {SCALES_URL}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching data from {SCALES_URL}: {err}")
