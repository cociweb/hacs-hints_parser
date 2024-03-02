import logging
import json
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

class EntityParserSensor(Entity):
    def __init__(self, hass, options):
        self._state = None
        self.hass = hass
        self.options = options

    @property
    def name(self):
        return 'HINTS Parser'

    @property
    def state(self):
        return self._state

    def update(self):
        domains = self.options.get("selected_domains", [])
        _LOGGER.info("HINTS selected domains: %s", domains)
        self.hass.states.async_set('sensor.hints_parser', domains, {})
        return True

    def read_registry_file(self, filename):
        path = self.hass.config.path(f".storage/{filename}")

        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)

        return data
