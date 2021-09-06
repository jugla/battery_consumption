"""The Compensation integration."""
import logging
import warnings

# import numpy as np
import voluptuous as vol
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import (
    CONF_ATTRIBUTE,
    CONF_SOURCE,
    CONF_UNIQUE_ID,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_BATTERY_CONSUMPTION,
    CONF_PRECISION,
    DATA_BATTERY_CONSUMPTION,
    DEFAULT_PRECISION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


BATTERY_CONSUMPTION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCE): cv.entity_id,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_ATTRIBUTE): cv.string,
        vol.Optional(CONF_PRECISION, default=DEFAULT_PRECISION): cv.positive_int,
        vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Optional(
            CONF_BATTERY_CAPACITY, default=DEFAULT_PRECISION
        ): cv.positive_float,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: BATTERY_CONSUMPTION_SCHEMA})},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Batery Consumption sensor."""
    hass.data[DATA_BATTERY_CONSUMPTION] = {}

    for battery_consumption, conf in config.get(DOMAIN).items():
        _LOGGER.debug("Setup %s.%s", DOMAIN, battery_consumption)

        data = {k: v for k, v in conf.items()}

        hass.data[DATA_BATTERY_CONSUMPTION][battery_consumption] = data

        hass.async_create_task(
            async_load_platform(
                hass,
                SENSOR_DOMAIN,
                DOMAIN,
                {CONF_BATTERY_CONSUMPTION: battery_consumption},
                config,
            )
        )

    return True
