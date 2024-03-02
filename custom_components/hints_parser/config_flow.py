import logging
from homeassistant import config_entries, const
from homeassistant.helpers import config_validation as cv
import voluptuous as vol


_LOGGER = logging.getLogger(__name__)
from .const import (
    DOMAIN,
    CONF_SELECTED_DOMAINS,
    CONF_EXPOSED_ENTITIES,
    CONF_AREA_CHECK
)

class EntityParserConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1
    async def async_step_user(self, user_input=None):

        errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            title = "Selected domains: " + ", ".join(user_input["selected_domains"])
            return self.async_create_entry(title=title, data=user_input)

        # Get all unique domains from the current states
        domains = {state.domain for state in self.hass.states.async_all()}
        # Sort the domains in alphabetical order
        domains = sorted(domains)

        # Pre-select 'switch' and 'light' domains
        default_domains = [const.Platform.SWITCH, const.Platform.LIGHT, const.Platform.SENSOR]

        options = {domain: domain for domain in domains}

        data_schema = vol.Schema({
            vol.Required(CONF_SELECTED_DOMAINS, default=default_domains): cv.multi_select(options),
            vol.Optional(CONF_AREA_CHECK, default=True): cv.boolean,
            vol.Optional(CONF_EXPOSED_ENTITIES, default=False): cv.boolean
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
