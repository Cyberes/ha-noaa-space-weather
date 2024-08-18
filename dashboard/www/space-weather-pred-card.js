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
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        align-items: center;
        justify-items: center;
      }

        .prediction-item {
          text-align: center;
          /*margin-bottom: 16px;*/
          cursor: pointer;
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
          padding: 0 16px 2px 16px;
          text-align: center;
        }
        
        .card-subheader {
          padding: 0 16px 16px 16px;
          margin-bottom: 16px;
          text-align: center;
          font-style: italic;
          font-size: 15px;
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
        <div class="card-subheader">
            For ${this._getStateValue('sensor.space_weather_prediction_date_stamp')}
        </div>
        <div class="card-content">
          <div class="prediction-container">
            <div class="prediction-item" data-entity-id="sensor.space_weather_prediction_r_minorprob">
              <div class="prediction-label">R1-R2</div>
              <!-- TODO: what happens when "Scale" in JSON is not null? -->
              <!-- TODO: what happens when "Text" in JSON is not null? -->
              <div class="prediction-value">
                ${Math.round(parseFloat(this._getStateValue('sensor.space_weather_prediction_r_minorprob')))}%
              </div>
            </div>
            <div class="prediction-item" data-entity-id="sensor.space_weather_prediction_r_majorprob">
              <div class="prediction-label">R3-R5</div>
              <!-- TODO: what happens when "Scale" in JSON is not null? -->
              <!-- TODO: what happens when "Text" in JSON is not null? -->
              <div class="prediction-value">
                ${Math.round(parseFloat(this._getStateValue('sensor.space_weather_prediction_r_majorprob')))}%
              </div>
            </div>
            <div class="prediction-item" data-entity-id="sensor.space_weather_prediction_s_prob">
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
            <div class="prediction-item" data-entity-id="sensor.space_weather_prediction_g_scale">
              <div class="prediction-label">G Scale</div>
              <div class="prediction-value scale-value noaa_scale_bg_${this._getStateValue('sensor.space_weather_prediction_g_scale')}">
                G${this._getStateValue('sensor.space_weather_prediction_g_scale')}
              </div>
            </div>
          </div>
        </div>
      </ha-card>
    `;
        this._attachClickListeners();
    }

    _getStateValue(entityId) {
        const state = this._hass.states[entityId];
        return state ? state.state : '';
    }

    _getAttribute(entityId, attribute) {
        const state = this._hass.states[entityId];
        return state ? state.attributes[attribute] : '';
    }

    _getNumericState(entityId) {
        const stateValue = this._getStateValue(entityId);
        return stateValue.substring(1);
    }

    getCardSize() {
        return 5;
    }

    _attachClickListeners() {
        const scaleItems = this.shadowRoot.querySelectorAll('.prediction-item');
        scaleItems.forEach(item => {
            item.addEventListener('click', () => {
                const entityId = item.dataset.entityId;
                this._handleClick(entityId);
            });
        });
    }

    _handleClick(entityId) {
        const event = new Event('hass-more-info', {composed: true});
        event.detail = {entityId};
        this.dispatchEvent(event);
    }
}

customElements.define('space-weather-prediction-card-1day', SpaceWeatherPredictionCard);
