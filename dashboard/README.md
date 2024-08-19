## Install
1. Copy files from `www` to `config/www`
2. Dashboard > Edit > 3 button menu > Manage resources
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
