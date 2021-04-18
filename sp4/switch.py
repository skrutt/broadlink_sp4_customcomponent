"""Support for Clas Ohlson devices."""
import binascii
from datetime import timedelta
import logging
import socket

from . import sp4 as _sp4
import voluptuous as vol

from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    SwitchEntity,
)
from homeassistant.const import (
    CONF_COMMAND_OFF,
    CONF_COMMAND_ON,
    CONF_FRIENDLY_NAME,
    CONF_HOST,
    CONF_MAC,
    CONF_SWITCHES,
    CONF_TIMEOUT,
    CONF_TYPE,
    STATE_ON,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import Throttle, slugify

from . import async_setup_service, data_packet

_LOGGER = logging.getLogger(__name__)

TIME_BETWEEN_UPDATES = timedelta(seconds=5)

DEFAULT_NAME = "Clas switch"
DEFAULT_TIMEOUT = 10
DEFAULT_RETRY = 2
CONF_SLOTS = "slots"
CONF_RETRY = "retry"

SP4_TYPES = ["sp4"]

SWITCH_TYPES = SP4_TYPES

SWITCH_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_COMMAND_OFF): data_packet,
        vol.Optional(CONF_COMMAND_ON): data_packet,
        vol.Optional(CONF_FRIENDLY_NAME): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_SWITCHES, default={}): cv.schema_with_slug_keys(
            SWITCH_SCHEMA
        ),
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TYPE, default=SWITCH_TYPES[0]): vol.In(SWITCH_TYPES),
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(CONF_RETRY, default=DEFAULT_RETRY): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Clas Ohlson switches."""

    devices = config.get(CONF_SWITCHES)
    slots = config.get("slots", {})
    ip_addr = config.get(CONF_HOST)
    friendly_name = config.get(CONF_FRIENDLY_NAME)
    mac_addr = binascii.unhexlify(config.get(CONF_MAC).encode().replace(b":", b""))
    switch_type = config.get(CONF_TYPE)
    retry_times = config.get(CONF_RETRY)

    def _get_mp1_slot_name(switch_friendly_name, slot):
        """Get slot name."""
        if not slots[f"slot_{slot}"]:
            return f"{switch_friendly_name} slot {slot}"
        return slots[f"slot_{slot}"]

    if switch_type in SP4_TYPES:
        clas_device = _sp4.sp4((ip_addr, 80), mac_addr, 0x7579, None)
        switches = [ClasSP4(friendly_name, clas_device, retry_times)]
    
    clas_device.timeout = config.get(CONF_TIMEOUT)
    try:
        clas_device.auth()
    except OSError:
        _LOGGER.error("Failed to connect to device")

    add_entities(switches)

class ClasSP4(SwitchEntity):
    """Representation of an Broadlink switch."""
    def __init__(self, name, device, haskey = 0):
        """Initialize the switch."""
        self._haskey = haskey
        
        self.entity_id = ENTITY_ID_FORMAT.format(name)
        self._name = name
        self._dev = device
        self._unique_id = 'sp4' + self._dev.mac.hex()
        #set to true if we failed to set state
        self._update_state = 0
        self._safe_state = {'pwr':0, 'ntlight': 0, 'indicator':0, 'ntlbrightness':60}
        self._state = self._safe_state
        self._is_available = True
        _LOGGER.info("Init done")
        
    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id
    @property
    def name(self):
        """Return the name of the switch."""
        _LOGGER.info("Name called")
        return self._name

    @property
    def assumed_state(self):
        """Return true if unable to access real state of entity."""
        _LOGGER.info("assumed_state called")
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        _LOGGER.info("available called")
        return True

    @property
    def should_poll(self):
        """Return the polling state."""
        _LOGGER.info("should_poll called")
        return True

    @property
    def is_on(self):
        """Return true if device is on."""
        _LOGGER.info("is_on called")
        try:
            # TODO: write code...
            return self._state['pwr']
        except:
            self._state = self._safe_state #Bad state, update to default state
            return self._state['pwr']
        
    @property
    def device_state_attributes(self):
        """Show state attributes in HASS"""
        _LOGGER.info("device_state_attributes called")
        attrs = {'ip_address': self._dev.host,
                 'mac': self._dev.mac.hex(),
                 'devtype': hex(self._dev.devtype),
                 'type': self._dev.type,
                 'timeout': self._dev.timeout,
                 'haskey': self._haskey
                 }
        
        attrs.update(self._state)
        return attrs

    def turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.info("turn_on called")
        try:
            self._state = self._dev.set_state(pwr=1)
        except:
            self._update_state = {'pwr': 1}
            _LOGGER.error("Except in turn_on")
        return

    def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.info("turn_off called")
        try:
            self._state = self._dev.set_state(pwr=0)
        except:
            self._update_state = {'pwr': 0}
            _LOGGER.error("Except in turn_off")
        return
    
    def update(self):
        """Synchronize state with switch."""    #Add parsing of all states
        _LOGGER.info("update called")
        if(not self._haskey):
            try:
                if(self._dev.auth()):
                    _LOGGER.info("late auth in update OK")
                    self.haskey = 1
                else:
                    _LOGGER.info("late auth in update FAIL")
            except:
                _LOGGER.error("except in update late auth!!!!!")
        try:
            
            if(self._update_state):
                self._state = self._dev.set_state_dict(self._update_state)
                self._update_state = 0
            else:
                self._state = self._dev.get_state()
        except:
            _LOGGER.error("except in update")
