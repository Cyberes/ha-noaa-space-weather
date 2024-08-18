class SpaceWeatherPredictionCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({mode: 'open'});
    }

    setConfig(config) {
        this._config = config;
    }

    set hass(hass) {
        this._hass = hass;
        this.render();
    }

    render() {
        if (!this.shadowRoot) return;

        this.shadowRoot.innerHTML = `
      <style>
      /* TODO: unify this with the other card */
      
        .prediction-container {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .prediction-item {
          text-align: center;
          margin-bottom: 16px;
        }

        .prediction-label {
          font-weight: bold;
          margin-bottom: 8px;
        }

        .prediction-value {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 4px;
          padding: 8px;
          border-radius: 4px;
        }

        .noaa_scale_bg_5 {
          background-color: #C80000;
        }
        .noaa_scale_bg_4 {
          background-color: #FF0000;
        }
        .noaa_scale_bg_3 {
          background-color: #FF9600;
        }
        .noaa_scale_bg_2 {
          background-color: #FFC800;
        }
        .noaa_scale_bg_1 {
          background-color: #F6EB14;
        }
        .noaa_scale_bg_0 {
          background-color: #92D050;
        }

        .card-header {
          font-size: 20px;
          font-weight: bold;
          padding: 16px;
          margin-bottom: 16px;
          text-align: center;
        }
        
        .scale-value {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 4px;
          padding: 8px;
          border-radius: 4px;
        }
        
        a {
          text-decoration: none;
          color: inherit;
        }
      </style>

      <ha-card>
        <div class="card-header">Space Weather Predictions</div>
        <div class="card-content">
          <div class="prediction-container">
            <div class="prediction-item">
              <div class="prediction-label">R1-R2</div>
              <!-- TODO: what happens when "Scale" in JSON is not null? -->
              <!-- TODO: what happens when "Text" in JSON is not null? -->
              <div class="prediction-value">
                ${Math.round(parseFloat(this._getStateValue('sensor.space_weather_prediction_r_minorprob')))}%
              </div>
            </div>
            <div class="prediction-item">
              <div class="prediction-label">R3-R5</div>
              <!-- TODO: what happens when "Scale" in JSON is not null? -->
              <!-- TODO: what happens when "Text" in JSON is not null? -->
              <div class="prediction-value">
                ${Math.round(parseFloat(this._getStateValue('sensor.space_weather_prediction_r_majorprob')))}%
              </div>
            </div>
            <div class="prediction-item">
              <div class="prediction-label">S1 or Greater</div>
              <!-- TODO: what happens when "Scale" in JSON is not null? -->
              <!-- TODO: what happens when "Text" in JSON is not null? -->
              <div class="prediction-value">
                ${Math.round(parseFloat(this._getStateValue('sensor.space_weather_prediction_s_prob')))}%
              </div>
            </div>
            <!-- <div class="prediction-item">
              <div class="prediction-label">S Probability</div>
              <div class="prediction-value">
                ${this._getStateValue('sensor.space_weather_prediction_s_scale')}
              </div>
            </div> -->
            <div class="prediction-item">
              <div class="prediction-label">G Scale</div>
              <div class="prediction-value scale-value noaa_scale_bg_${this._getStateValue('sensor.space_weather_prediction_g_scale')}">
                G${this._getStateValue('sensor.space_weather_prediction_g_scale')}
              </div>
            </div>
          </div>
        </div>
      </ha-card>
    `;
    }

    _getStateValue(entityId) {
        const state = this._hass.states[entityId];
        return state ? state.state : '';
    }

    _getNumericState(entityId) {
        const stateValue = this._getStateValue(entityId);
        return stateValue.substring(1);
    }

    getCardSize() {
        return 5;
    }
}

customElements.define('space-weather-prediction-card', SpaceWeatherPredictionCard);
