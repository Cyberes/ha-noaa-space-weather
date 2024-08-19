This is an MQTT sensor to send NOAA space weather data to Home Assistant. Fetching the data requires a login to NASA's EarthData which is done through Selenium and the Chrome browser.

## Install

1. Create an account at <https://urs.earthdata.nasa.gov>
2. `pip install -r requirements.txt`
3. `sudo apt install p7zip-full`

### Google Chrome

If you don't have Google Chrome installed (used to log into the NASA site), here's how to install it.

```shell
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install ./google-chrome-stable_current_amd64.deb
```

## Run

The lat/lon range is used to pick the region of the planet for generating statistics, for example your home state. To

```shell
LAT_RANGE_MIN=<lower range for lat bounding box> \
LAT_RANGE_MAX=<upper range for lat bounding box> \
LON_RANGE_MIN=<lower range for lon bounding box> \
LON_RANGE_MAX=<upper range for lon bounding box> \
CDDIS_USERNAME=<username> CDDIS_PASSWORD=<password> \
MQTT_BROKER_HOST="<Home Assistant IP>" MQTT_BROKER_PORT=1883 MQTT_USERNAME="user" MQTT_PASSWORD="<password>" \
python3 main.py
```

An example systemd service file is provided.

### Home Assistant MQTT Config

```yaml
mqtt:
  - state_topic:         "space-weather/vtec"
    name:                "VTEC"
    unit_of_measurement: "(10^16 el) / m^2"
    state_class:         measurement
    unique_id:           space_weather_vtec
```

## Data

### VTEC

<https://www.spaceweather.gov/products/us-total-electron-content>

Unit: `(10^16 el) / m^2`

VTEC, or Vertical TEC, is a specific type of TEC measurement that is taken along a path extending
vertically from the Earth's surface to the edge of the atmosphere. So essentially, VTEC is a subset of TEC, with the
difference lying in the specific path along which the measurement is taken.

Updated hourly.
