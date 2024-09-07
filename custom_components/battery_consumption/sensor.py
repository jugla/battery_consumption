"""Support for compensation sensor."""
import logging
import datetime
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ATTRIBUTE,
    CONF_SOURCE,
    CONF_UNIQUE_ID,
    CONF_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_BATTERY_CONSUMPTION,
    CONF_PRECISION,
    DATA_BATTERY_CONSUMPTION,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)

# attributes
# indicate the source for battery
ATTR_SOURCE = "source"
ATTR_SOURCE_ATTRIBUTE = "source_attribute"
# different attributes in % (battery level)
ATTR_PREVIOUS_MONITORED_VALUE = "previous_value"
ATTR_CURRENT_VARIATION = "variation"
ATTR_CURRENT_CHARGE = "battery_charge"
ATTR_CURRENT_DISCHARGE = "battery_discharge"
# different attributes in Wh (energy)
ATTR_CURRENT_VARIATION_ENERGY = "energy_variation"
ATTR_CURRENT_CHARGE_ENERGY = "energy_charge"
ATTR_CURRENT_DISCHARGE_ENERGY = "energy_discharge"
ATTR_TOTAL_CHARGE = "total_charge"
ATTR_TOTAL_DISCHARGE = "total_discharge"
ATTR_TOTAL_CHARGE_ENERGY = "total_energy_charge"
ATTR_TOTAL_DISCHARGE_ENERGY = "total_energy_discharge"
ATTR_CAPACITY_UNIT = "capacity_unit"
ATTR_CAPACITY = "capacity"
ATTR_ENERGY_LEVEL = "energy_level"
# different attributes in time
ATTR_LAST_UPDATED = "last_updated"
ATTR_PREVIOUS_LAST_UPDATED = "previous_last_updated"
ATTR_DELTA_LAST_UPDATED = "delta_last_updated_in_minutes"
# different attributes in W (power)
ATTR_CURRENT_POWER = "instant_power"


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Battery Consumption sensor."""
    if discovery_info is None:
        return

    battery_consumption = discovery_info[CONF_BATTERY_CONSUMPTION]
    conf = hass.data[DATA_BATTERY_CONSUMPTION][battery_consumption]

    source = conf[CONF_SOURCE]
    attribute = conf.get(CONF_ATTRIBUTE)
    name = f"{DEFAULT_NAME}_{source}"
    if attribute is not None:
        name = f"{name}_{attribute}"

    async_add_entities(
        [
            BatteryConsumptionSensor(
                conf.get(CONF_UNIQUE_ID),
                name,
                source,
                attribute,
                conf[CONF_PRECISION],
                conf.get(CONF_BATTERY_CAPACITY),
                conf.get(CONF_UNIT_OF_MEASUREMENT),
            )
        ]
    )


def format_receive_value(value):
    """format if pb then return None"""
    if value == None or value == STATE_UNKNOWN or value == STATE_UNAVAILABLE:
        return None
    else:
        return value

def format_receive_value_date(value):
    """format if pb then return None"""
    if value == None or value == STATE_UNKNOWN or value == STATE_UNAVAILABLE:
        return None
    else:
        return datetime.fromisoformat(value)

def format_receive_value_float(value):
    """format if pb then return None"""
    if value == None or value == STATE_UNKNOWN or value == STATE_UNAVAILABLE:
        return None
    else:
        return float(value)

def format_receive_value_zero(value):
    """format if pb then return 0.0"""
    if value == None or value == STATE_UNKNOWN or value == STATE_UNAVAILABLE:
        return float(0.0)
    else:
        return float(value)


class BatteryConsumptionSensor(RestoreEntity, SensorEntity):
    """Representation of a BatteryConsumptionSensor."""

    def __init__(
        self,
        unique_id,
        name,
        source,
        attribute,
        precision,
        battery_capacity,
        unit_of_measurement,
    ):
        """Initialize the BatteryConsumptionSensor."""
        self._unique_id = unique_id
        self._name = name
        self._source_entity_id = source
        self._source_attribute = attribute
        self._precision = precision
        self._battery_capacity = battery_capacity
        self._unit_of_measurement = unit_of_measurement

        # state values
        self._state = None
        self._last_updated = None
        self._previous_state = None
        self._previous_last_updated = None

        # state value : induced value
        self._delta = 0.0
        self._delta_last_updated = 0.0

        # state value : cumulative value
        self._cumulative_charge = 0.0
        self._cumulative_discharge = 0.0

    async def async_added_to_hass(self):
        """Handle added to Hass."""
        # restore from previous run
        await super().async_added_to_hass()
        state_recorded = await self.async_get_last_state()
        if state_recorded:
            # state
            self._state = format_receive_value_float(state_recorded.state)
            self._last_updated = state_recorded.last_updated
            # previous
            self._previous_state = format_receive_value(
                state_recorded.attributes.get(ATTR_PREVIOUS_MONITORED_VALUE)
            )
            self._previous_last_updated = format_receive_value_date(
                state_recorded.attributes.get(ATTR_PREVIOUS_LAST_UPDATED)
            )
            #recompute induced data from the 4th above
            self._compute_induced_data()

            # cumulative
            self._cumulative_charge = format_receive_value_zero(
                state_recorded.attributes.get(ATTR_TOTAL_CHARGE)
            )
            self._cumulative_discharge = format_receive_value_zero(
                state_recorded.attributes.get(ATTR_TOTAL_DISCHARGE)
            )




        # listen to source ID
        async_track_state_change_event(
            self.hass,
            [self._source_entity_id],
            self._async_battery_consumption_sensor_state_listener,
        )


    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        ret = {
            ATTR_SOURCE: self._source_entity_id,
        }
        if self._source_attribute:
            ret[ATTR_SOURCE_ATTRIBUTE] = self._source_attribute
        ret[ATTR_PREVIOUS_MONITORED_VALUE] = self._previous_state

        # print update time
        ret[ATTR_LAST_UPDATED] = self._last_updated
        ret[ATTR_PREVIOUS_LAST_UPDATED] = self._previous_last_updated
        # set in minute
        ret[ATTR_DELTA_LAST_UPDATED] = self._delta_last_updated / 60

        # variation %
        ret[ATTR_CURRENT_VARIATION] = self._delta
        if self._delta < 0:
            ret[ATTR_CURRENT_CHARGE] = 0
            ret[ATTR_CURRENT_DISCHARGE] = -self._delta
        else:
            ret[ATTR_CURRENT_CHARGE] = self._delta
            ret[ATTR_CURRENT_DISCHARGE] = 0

        ret[ATTR_TOTAL_CHARGE] = self._cumulative_charge
        ret[ATTR_TOTAL_DISCHARGE] = self._cumulative_discharge

        if self._battery_capacity != None:
            ret[ATTR_CAPACITY_UNIT] = self._unit_of_measurement
            ret[ATTR_CAPACITY] = self._battery_capacity

            ret[ATTR_ENERGY_LEVEL] = (
                self._state * self._battery_capacity / 100
            )

            ret[ATTR_CURRENT_VARIATION_ENERGY] = (
                self._delta * self._battery_capacity / 100
            )
            if self._delta < 0:
                ret[ATTR_CURRENT_CHARGE_ENERGY] = 0
                ret[ATTR_CURRENT_DISCHARGE_ENERGY] = (
                    -self._delta * self._battery_capacity / 100
                )
            else:
                ret[ATTR_CURRENT_CHARGE_ENERGY] = (
                    self._delta * self._battery_capacity / 100
                )
                ret[ATTR_CURRENT_DISCHARGE_ENERGY] = 0

            ret[ATTR_TOTAL_CHARGE_ENERGY] = (
                self._cumulative_charge * self._battery_capacity / 100
            )
            ret[ATTR_TOTAL_DISCHARGE_ENERGY] = (
                self._cumulative_discharge * self._battery_capacity / 100
            )


            try:
                # delta in % --> convert in Wh/kWh/MWh , 
                # delta_last_updated in second --> convert into h
                ret[ATTR_CURRENT_POWER] = (
                    ( self._delta * self._battery_capacity / 100 )
                    /
                    ( self._delta_last_updated / 3600 )
                )
            except:
                # manage divide by 0
                ret[ATTR_CURRENT_POWER] = 0.0

        return ret

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return "%"

    def _compute_induced_data (self):
        if (
            self._previous_state != None
            and self._state != None
            and self._previous_state != STATE_UNKNOWN
            and self._state != STATE_UNKNOWN
        ):
            try:
                self._delta = self._state - self._previous_state
            except:
                self._delta = 0
                _LOGGER.warning(
                    "%s state or %s previous is not numerical",
                    self._state,
                    self._previous_state,
                )


            try:
                delta_last_updated = self._last_updated - self._previous_last_updated
                self._delta_last_updated = delta_last_updated.total_seconds()
            except:
                self._delta_last_updated = 0.0
                _LOGGER.warning(
                    "%s last_updated or %s previous_last_updated is not numerical",
                    self._last_updated,
                    self._previous_last_updated,
                )


        else:
            self._delta = 0
            self._delta_last_updated = 0.0

    def _compute_cumulative_data (self):
        if self._delta < 0:
            self._cumulative_discharge = self._cumulative_discharge - self._delta
        else:
            self._cumulative_charge = self._cumulative_charge + self._delta



    def _compute_new_state_and_attribute(self, value, last_updated):
        """Compute new state of the sensor and its attribute"""
        #previous
        self._previous_state = self._state
        self._previous_last_updated = self._last_updated
        #new state
        self._state = round(value, self._precision)
        self._last_updated = last_updated
        #compute data from the 4th above
        self._compute_induced_data()
        self._compute_cumulative_data()

    @callback
    def _async_battery_consumption_sensor_state_listener(self, event):
        """Handle sensor state changes."""
        new_state_valid = False
        value = None
        # retrieve state
        new_state = event.data.get("new_state")
        last_updated = new_state.last_updated
        if new_state is None:
            return

        try:
            if self._source_attribute:
                value = float(new_state.attributes.get(self._source_attribute))
            else:
                value = (
                    None if new_state.state == STATE_UNKNOWN else float(new_state.state)
                )
            if value != None:
                new_state_valid = True

        except (ValueError, TypeError):
            # self._state = None
            if self._source_attribute:
                _LOGGER.warning(
                    "%s attribute %s is not numerical",
                    self._source_entity_id,
                    self._source_attribute,
                )
            else:
                _LOGGER.warning("%s state is not numerical", self._source_entity_id)

        if new_state_valid == True:
            self._compute_new_state_and_attribute(value, last_updated)
            self.async_write_ha_state()
