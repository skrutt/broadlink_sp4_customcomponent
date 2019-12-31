
"""Support for Broadlink RM devices."""
from homeassistant.components.switch import SwitchDevice
from homeassistant.components.switch import ENTITY_ID_FORMAT
import logging
from . import sp4 as _sp4

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Broadlink switches."""
    
    broadlink_device = _sp4.sp4(('192.168.10.6', 80), b''.fromhex('4bb02da7df24'), 0x7579, timeout = 5) #Add device 1   EDIT
    broadlink_device2 = _sp4.sp4(('192.168.10.12', 80), b''.fromhex('ecb02da7df24'), 0x7579, timeout = 5) #Add device 2   EDIT
    
    auth = 0
    try:
        _LOGGER.info(broadlink_device.auth())    #Auth device 1   EDIT
        _LOGGER.info(broadlink_device2.auth())   #Auth device 2   EDIT
        _LOGGER.info("That was auth response")
        auth = 1
    except:
        _LOGGER.info("Failed auth response")
        
    
    switches = [BroadlinkSP4('guestroom', broadlink_device, auth), BroadlinkSP4('Computercorner', broadlink_device2, auth)] #Add all devices, with names   EDIT
    
    add_entities(switches)
    _LOGGER.info("Setup done")

class BroadlinkSP4(SwitchDevice):
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
    