# broadlink_sp4_customcomponent
First try for an integration of custom component with added broadlink sp4 support

This is a custom component, and a rough one at that. 

You will get a warning in your log about using an untested custom component,
and MANY posts in you log about status updates from the component working. 

This is not really a problem, but maybe not so pretty. 

But it helps any troubleshooting, so until there have been more testing, it will most likely stay for now. 



INSTRUCTIONS:

Copy directory sp4 into your directory custom_components in your config directory. (Thats alot of directorys... your config dir is where your configuration.yaml is. custom_components might need to be created if you have not done so already)

You also need to add this:

switch:
  platform: sp4
  
to your configuration.yaml. Note that github seems to be mangling the newline, you might not be able to copy this text directly from here.

Then there is configuration, now you need to add your devices in switch/sp4.py

In this python file there are lines with "EDIT" on the end, focus on these. In the file as uploaded there are two devices configured, guestroom and computercorner. Hopefully this should get you started, you can add or remove devices and auth if you have more or less devices. It's these lines in the beginning:


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

This is of course not standard changing the python directly, nor is that the modded I/O lib for sp4 broadlink switch is included right there instead of as a dependency, but this works for now and is reasonably understandable?


