## Install
1. Copy files from `www` to `config/www`
2. `Dashboard` > `Edit` > 3 button menu > `Manage resources`
3. Enter these 3 resources:
   ```
   /local/space-weather-24hr-max-card.js?v=1
   /local/space-weather-card.js?v=1
   /local/space-weather-pred-card.js?v=1
   ```
## Use
To add these custom cards, create a card of the "Manual" type.

```
type: space-weather-current
type: space-weather-prediction-1day
type: space-weather-24hr-max
```

## Example VTEC Graph

In the example dashboard seen in `dashboard.png`, the VTEC graph uses components from [mini-graph-card](https://github.com/kalkih/mini-graph-card). Use the following definition:

```yaml
type: custom:mini-graph-card
entities:
  - entity: sensor.space_weather_vtec
color_thresholds:
  - value: 0
    color: '#030586'
  - value: 10
    color: '#0506e6'
  - value: 20
    color: '#004efd'
  - value: 30
    color: '#00b5fd'
  - value: 40
    color: '#14fde7'
  - value: 50
    color: '#6ffd8d'
  - value: 60
    color: '#e9fc13'
  - value: 70
    color: '#fbaf03'
  - value: 80
    color: '#fb4801'
  - value: 90
    color: '#da0302'
  - value: 100
    color: '#750305'
```