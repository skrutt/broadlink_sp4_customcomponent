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
```
switch:
 - platform: clas
   host: IP_ADDR_OF_SWITCH
   mac: MAC_OF_SWITCH
   type: sp4
```
to your configuration.yaml. Note that github seems to be mangling the newline, you might not be able to copy this text directly from here.

This is of course not standard changing the python directly, nor is that the modded I/O lib for sp4 broadlink switch is included right there instead of as a dependency, but this works for now and is reasonably understandable?
