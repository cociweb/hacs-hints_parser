from homeassistant.components.http import HomeAssistantView

from .const import (
    DOMAIN,
    CONF_EXPOSED_ENTITIES,
    CONF_SELECTED_DOMAINS,
    CONF_AREA_CHECK
)

class EntityParserAPI(HomeAssistantView):
    url = "/api/hints_parser"
    name = "api:hints_parser"
    requires_auth = True  # This ensures the API endpoint is secured

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        # Get the instance of the EntityParserSensor
        sensor = self.hass.data[DOMAIN]

        if sensor is None:
            return self.json_message('HINTS-Parser sensor instance not found', status_code=404)

        # Call the update method
        sensor.update()

        # Parse the information from the registry files
        entity_d = sensor.read_registry_file("core.entity_registry")
        area_d = sensor.read_registry_file("core.area_registry")
        device_d = sensor.read_registry_file("core.device_registry")
        out = {'entity': []}  # Initialize 'entity' as an empty list
        out_device = {}

        # Get the selected domains from the integration's options
        domains = sensor.options.get(CONF_SELECTED_DOMAINS, [])
        only_exposed = sensor.options.get(CONF_EXPOSED_ENTITIES, [])
        include_areas = sensor.options.get(CONF_AREA_CHECK, [])

        for device in device_d['data']['devices']:
            device_id = device['id']
            device_name = device.get('name', '')
            device_user_name = device.get('name_by_user', '')

            names = {}

            if device_name:
                name = device_name
                names['name_original'] = device_name
            else:
                name = None
                names['name_original'] = None

            if device_user_name:
                name = device_user_name
                names['name_by_user'] = device_user_name
            else:
                name = name
                names['name_by_user'] = None

            device_data = {
                'name': name,
                'name_original': names['name_original'],
                'name_by_user': names['name_by_user']
            }

            #out_device.append(device_id)
            out_device[device_id] = device_data

        for entity in entity_d['data']['entities']:
            prepared = False
            domain_filter = entity['entity_id'].split(".")[0]

            if only_exposed and entity['options']['conversation'].get('should_expose', ''):
                prepared = True
            elif not only_exposed:
                prepared = True

            if domain_filter in domains and prepared:
                prepared = True
            else:
                prepared = False

            if prepared:
                entity_id = entity['entity_id']
                name = entity.get('name', '')
                aliases = entity.get('aliases', [])
                orig_name = entity.get('original_name', '')
                device_id = entity.get('device_id', '')

                entity_data = {
                    'id': entity_id,
                }

                if not name:
                #    continue  # skip to the next iteration
                    if not orig_name:
                        continue
                    else:
                        entity_data['name'] = None
                else:
                    entity_data['name'] = name

                if orig_name:
                    if device_id and out_device[device_id]['name']:
                        if orig_name.startswith(out_device[device_id]['name']):
                            entity_data['alter_name'] = orig_name
                        else:
                            entity_data['alter_name'] = out_device[device_id]['name']+" "+orig_name
                    else:
                        entity_data['alter_name'] = orig_name
                else:
                    entity_data['alter_name'] = None


                if aliases:
                    entity_data['aliases'] = "|".join(aliases)
                else:
                    entity_data['aliases'] = None

                out['entity'].append(entity_data)

        if include_areas:
            out['area'] = []  # Initialize 'area' as an empty list only when include_areas is True
            for area in area_d['data']['areas']:
                area_id = area['id']
                area_name = area.get('name', '')
                area_aliases = area.get('aliases', [])

                if area_name or area_aliases:
                    area_data = {
                        'id': area_id,
                    }

                    if area_name:
                        area_data['name'] = area_name
                    else:
                        area_data['name'] = None

                    if aliases:
                        area_data['aliases'] = " ".join(area_aliases)
                    else:
                        area_data['aliases'] = None

                    out['area'].append(area_data)
                else:
                    continue


        # Return the parsed information as JSON
        return self.json(out)

