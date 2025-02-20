"""

This is a docstring placeholder.

This is where we will describe what this module does

"""
import asyncio
import logging
from datetime import timedelta
from typing import List

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.sensor import SensorDeviceClass, RestoreSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent, PERCENTAGE, UnitOfPower, UnitOfEnergy)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval

from custom_components.solis_modbus.const import DOMAIN, CONTROLLER, VERSION, POLL_INTERVAL_SECONDS, MANUFACTURER, \
    MODEL, VALUES, NUMBER_ENTITIES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry: ConfigEntry, async_add_devices):
    """Set up the number platform."""
    modbus_controller = hass.data[DOMAIN][CONTROLLER]
    # We only want this platform to be set up via discovery.
    _LOGGER.info("Options %s", len(config_entry.options))

    platform_config = config_entry.data or {}
    if len(config_entry.options) > 0:
        platform_config = config_entry.options

    _LOGGER.info(f"Solis platform_config: {platform_config}")

    # fmt: off

    numberEntities: List[SolisNumberEntity] = []

    numbers = [
        {"type": "SNE", "name": "Solis Time-Charging Charge Current", "register": 43141,
         "default": 50.0, "multiplier": 10,
         "min_val": 0, "max_val": 135, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
         "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},
        {"type": "SNE", "name": "Solis Time-Charging Discharge Current", "register": 43142,
         "default": 50.0, "multiplier": 10,
         "min_val": 0, "max_val": 135, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
         "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},
        {"type": "SNE", "name": "Solis Backup SOC", "register": 43024,
         "default": 80.0, "multiplier": 1,
         "min_val": 0, "max_val": 100, "step": 1,
         "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Battery Force-charge Power Limitation", "register": 43027,
         "default": 3000.0, "multiplier": 0.1,
         "min_val": 0, "max_val": 6000, "step": 1,
         "unit_of_measurement": UnitOfPower.WATT, "enabled": True},

        {"type": "SNE", "name": "Solis Overcharge SOC", "register": 43010,
         "default": 90, "multiplier": 1,
         "min_val": 70, "max_val": 100, "step": 1,
         "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Overdischarge SOC", "register": 43011,
         "default": 20, "multiplier": 1,
         "min_val": 5, "max_val": 40, "step": 1,
         "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Force Charge SOC", "register": 43018,
         "default": 10, "multiplier": 1,
         "min_val": 0, "max_val": 100, "step": 1,
         "unit_of_measurement": PERCENTAGE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 1) SOC", "register": 43708,
         "default": 10, "multiplier": 1,
         "min_val": 0, "max_val": 100, "step": 1,
         "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 1) Current", "register": 43709,
         "default": 16.0, "multiplier": 10,
         "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
         "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 2) SOC", "register": 43715,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 2) Current", "register": 43716,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 3) SOC", "register": 43722,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 3) Current", "register": 43723,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 4) SOC", "register": 43729,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 4) Current", "register": 43730,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 5) SOC", "register": 43736,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 5) Current", "register": 43737,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 6) SOC", "register": 43743,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Charge (Slot 6) Current", "register": 43744,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 1) SOC", "register": 43750,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 1) Current", "register": 43751,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 2) SOC", "register": 43757,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 2) Current", "register": 43758,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 3) SOC", "register": 43764,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 3) Current", "register": 43765,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 4) SOC", "register": 43771,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 4) Current", "register": 43772,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 5) SOC", "register": 43778,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 5) Current", "register": 43779,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 6) SOC", "register": 43785,
            "default": 10, "multiplier": 1,
            "min_val": 0, "max_val": 100, "step": 1,
            "unit_of_measurement": PERCENTAGE, "enabled": True},
        {"type": "SNE", "name": "Solis Grid Charging Discharge (Slot 6) Current", "register": 43786,
            "default": 16.0, "multiplier": 10,
            "min_val": 0, "max_val": 50, "step": 0.1, "device_class": SensorDeviceClass.CURRENT,
            "unit_of_measurement": UnitOfElectricCurrent.AMPERE, "enabled": True},

        {"type": "SNE", "name": "Solis Peak-shaving max usable grid power", "register": 43488,
         "default": 16000.0, "multiplier": 100,
         "min_val": 0, "max_val": 16000, "step": 100,
         "unit_of_measurement": UnitOfPower.WATT, "enabled": True},
        {"type": "SNE", "name": "Solis Battery Capacity", "register": 43019,
         "default": 100, "multiplier": 1,
         "min_val": 50, "max_val": 500, "step": 1,
         "unit_of_measurement": UnitOfEnergy.WATT_HOUR, "enabled": True},
    ]

    for entity_definition in numbers:
        type = entity_definition["type"]
        if type == "SNE":
            numberEntities.append(SolisNumberEntity(hass, modbus_controller, entity_definition))
    hass.data[DOMAIN][NUMBER_ENTITIES] = numberEntities
    async_add_devices(numberEntities, True)

    @callback
    def update(now):
        """Update Modbus data periodically."""
        controller = hass.data[DOMAIN][CONTROLLER]

        _LOGGER.info(f"calling number update for {len(hass.data[DOMAIN][NUMBER_ENTITIES])} groups")
        hass.create_task(get_modbus_updates(hass, controller))

    async def get_modbus_updates(hass, controller):
        if not controller.connected():
            await controller.connect()
        await asyncio.gather(
             *[asyncio.to_thread(entity.update) for entity in hass.data[DOMAIN][NUMBER_ENTITIES]]
         )


    async_track_time_interval(hass, update, timedelta(seconds=POLL_INTERVAL_SECONDS * 3))

    return True

    # fmt: on


class SolisNumberEntity(RestoreSensor, NumberEntity):
    """Representation of a Number entity."""

    def __init__(self, hass, modbus_controller, entity_definition):
        """Initialize the Number entity."""
        #
        # Visible Instance Attributes Outside Class
        self._hass = hass
        self._modbus_controller = modbus_controller
        self._register = entity_definition["register"]
        self._multiplier = entity_definition["multiplier"]

        # Hidden Inherited Instance Attributes
        self._attr_unique_id = "{}_{}_{}".format(DOMAIN, self._modbus_controller.host, self._register)
        self._attr_has_entity_name = True
        self._attr_name = entity_definition["name"]
        self._attr_native_value = entity_definition.get("default", None)
        self._attr_assumed_state = entity_definition.get("assumed", False)
        self._attr_available = False
        self.is_added_to_hass = False
        self._attr_device_class = entity_definition.get("device_class", None)
        self._attr_icon = entity_definition.get("icon", None)
        self._attr_mode = entity_definition.get("mode", NumberMode.AUTO)
        self._attr_native_unit_of_measurement = entity_definition.get("unit_of_measurement", None)
        self._attr_native_min_value = entity_definition.get("min_val", None)
        self._attr_native_max_value = entity_definition.get("max_val", None)
        self._attr_native_step = entity_definition.get("step", 1.0)
        self._attr_should_poll = False
        self._attr_entity_registry_enabled_default = entity_definition.get("enabled", False)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        state = await self.async_get_last_sensor_data()
        if state:
            self._attr_native_value = state.native_value
        self.is_added_to_hass = True

    def update(self):
        """Update Modbus data periodically."""
        self._attr_available = True

        value: float = self._hass.data[DOMAIN][VALUES][str(self._register)]
        self._hass.create_task(self.update_values(value))
        self.schedule_update_ha_state()

    async def update_values(self, value):
        if value == 0 and self._modbus_controller.connected():
            register_value = await self._modbus_controller.async_read_holding_register(self._register)
            value = register_value[0] if register_value else value

        self._attr_native_value = round(value / self._multiplier)


    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._hass.data[DOMAIN][CONTROLLER].host)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=f"{MANUFACTURER} {MODEL}",
            sw_version=VERSION,
        )

    def set_native_value(self, value):
        """Update the current value."""
        if self._attr_native_value == value:
            return

        self.hass.create_task(self._modbus_controller.async_write_holding_register(self._register, round(value * self._multiplier)))
        self._attr_native_value = value
        self.schedule_update_ha_state()
