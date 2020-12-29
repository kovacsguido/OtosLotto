"""The Otos Lotto Sensor [HUN] integration."""
import asyncio

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .sensor import OtosLottoAPI

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            vol.Schema({vol.Optional(CONF_NAME, default=DOMAIN): cv.string}),
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Otos Lotto Sensor [HUN] component from the configuration.yaml."""
    conf = config.get(DOMAIN)
    if conf:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, data=conf, context={"source": SOURCE_IMPORT}
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Otos Lotto Sensor [HUN] from a config entry."""
    hass.data.setdefault(DOMAIN, {}).update({entry.entry_id: OtosLottoAPI(DOMAIN)})

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
