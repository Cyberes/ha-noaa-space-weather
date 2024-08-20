class SpaceWeatherCard extends HTMLElement {
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
        .scale-container {
          display: flex;
          justify-content: space-around;
        }

        .scale-item {
          text-align: center;
        }

        .scale-label {
          font-weight: bold;
          margin-bottom: 8px;
        }

        .scale-value {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 4px;
          padding: 8px;
          border-radius: 4px;
        }

        .scale-text {
          font-size: 14px;
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

        a {
          text-decoration: none;
          color: inherit;
        }

        .card-header {
          font-size: 20px;
          font-weight: bold;
          padding: 16px;
          margin-bottom: 16px;
          text-align: center;
        }

        .scale-item {
          cursor: pointer;
        }
      </style>

      <ha-card>
        <div class="card-header">
            <a href="https://www.spaceweather.gov/noaa-scales-explanation" target="_blank">Space Weather Conditions</a>
        </div>
        <div class="card-content">
          <div class="scale-container">
            <div class="scale-item" data-entity-id="sensor.space_weather_scale_r">
            <div class="scale-value noaa_scale_bg_${this._getNumericState('sensor.space_weather_scale_r')}">
              ${this._getStateValue('sensor.space_weather_scale_r')}
            </div>
              <!-- <div class="scale-text">
                ${this._getStateAttribute('sensor.space_weather_scale_r', 'text')}
              </div> -->
            </div>
            <div class="scale-item" data-entity-id="sensor.space_weather_scale_s">
            <div class="scale-value noaa_scale_bg_${this._getNumericState('sensor.space_weather_scale_s')}">
              ${this._getStateValue('sensor.space_weather_scale_s')}
            </div>
              <!-- <div class="scale-text">
                ${this._getStateAttribute('sensor.space_weather_scale_s', 'text')}
              </div> -->
            </div>
            <div class="scale-item" data-entity-id="sensor.space_weather_scale_g">
            <div class="scale-value noaa_scale_bg_${this._getNumericState('sensor.space_weather_scale_g')}">
              ${this._getStateValue('sensor.space_weather_scale_g')}
            </div>
              <!-- <div class="scale-text">
                ${this._getStateAttribute('sensor.space_weather_scale_g', 'text')}
              </div> -->
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

    _getStateAttribute(entityId, attribute) {
        const state = this._hass.states[entityId];
        return state ? state.attributes[attribute] || '' : '';
    }

    _getNumericState(entityId) {
        const stateValue = this._getStateValue(entityId);
        return stateValue.substring(1);
    }

    _attachClickListeners() {
        const scaleItems = this.shadowRoot.querySelectorAll('.scale-item');
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

    getCardSize() {
        return 3;
    }
}

customElements.define('space-weather-current', SpaceWeatherCard);
