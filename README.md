# dtsu666-Emulator

This is a python library to emulate a dtsu666 smartmeter.

## Content:
`dtsu666emulator.py` the emulator.

`mqtt2smemulator.py` subscribes MQTT and converts the available data for the dtsu666 emulator.  
( I don't have per phase Power Factor or Reactive Power information, but I don't care about it, only the total power is relevant for me. )

## Background:
I have a Growatt SPH photovoltaik inverter, which expects an dtsu666 smartmeter to be installed in the main fuse box.
For it this is necessay, to know when to charge the battery, show correct energy flow status, and so on...

However, I already have this information from the smartmeter of the grid provider (see project: [AmsToMqttBridge](https://github.com/gskjold/AmsToMqttBridge)).
I find it redundant, to have two smartmeter installed, wanted to avoid the cabeling between smart meter and inverter.



This project takes the provided info from MQTT, modifies it as needed and emulates the dtsu666 smartmeter to be used by the growatt inverter.


## Dependency:
 - pymodbus 2.5.3 -- not working with version 3.0
