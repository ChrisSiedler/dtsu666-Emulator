# dtsu666-Emulator

This is a python library to emulate a CHINT DTSU666 smartmeter.

## Content:
`dtsu666emulator.py` the emulator.  
It's a modbus server, the client ( the Growatt inverter) can pull the data as needed.

`mqtt2smemulator.py` subscribes the available MQTT topics and converts the data for the dtsu666 emulator.  
( I don't have per phase Power Factor or Reactive Power information, but I don't care about it, only the total power is relevant for me. )

## Background:
I have a Growatt SPH photovoltaik inverter, which expects an DTSU666 smartmeter to be installed in the main fuse box.
For the inverter this is necessay, to know when to charge the battery, show correct energy flow status, and so on...

However, I already have this information available from the smartmeter of the grid provider (see project: [AmsToMqttBridge](https://github.com/gskjold/AmsToMqttBridge)).
So for me it would be redundant to have two smartmeter installed. Additionally I wanted to avoid the RS485 cabeling between smart meter and inverter.


This project takes the provided info from MQTT, modifies it as needed and emulates the dtsu666 smartmeter to be used by the growatt inverter.


## Current status:
It's working.  
I use this code on an RaspberryPi 3 with debian 11 and an cheap USB-RS485 adapter with an CH340 controller.

Now I see on the display of the inverter arrow symbols between the grid and the inverter,
Error 401 ( no smartmeter conected ) disapered and the inverter is now correctly calculating if the power goes to the grid or to the local load.


## Dependency:
 - pymodbus 2.5.3 -- not working with version 3.0
