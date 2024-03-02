import logging
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
import voluptuous as vol
from .sensor import EntityParserSensor
from .api import EntityParserAPI

_LOGGER = logging.getLogger(__name__)


from .const import (
    DOMAIN,
    STARTUP_MESSAGE
)

async def async_setup_entry(hass, config):
    # Get the selected domains from the integration's options
    if hass.data.get(DOMAIN) is None:
        _LOGGER.info(STARTUP_MESSAGE)
    options = config.data

    # Initialize the sensor
    sensor = EntityParserSensor(hass, options)

    # Add the sensor to the state machine
    hass.states.async_set('sensor.hints_parser', 'initialized', {})

    # Set the hints_parser data
    hass.data[DOMAIN] = sensor

    # Register the API endpoint
    hass.http.register_view(EntityParserAPI(hass))

    # Setup the sensor platform
    hass.helpers.discovery.load_platform(
        SENSOR_DOMAIN, DOMAIN, {}, config
    )

    return True