## Install

1. Copy `space_weather` to `config/custom_components`
2. Restart Home Assistant
3. Enable the custom component by going to `Devices & Services` > `Integrations` > `Add Integration` then searching for
   `space weather`. Or, add the following to your `configuration.yaml`:
    ```yaml
    sensor:
      - platform: space_weather
    ```
