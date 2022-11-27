# dtsu666-Emulator

This is a python library to emulate a dtsu666 smartmeter.

## Content:
`dtsu666emulator.py` the emulator.
`mqtt2smemulator.py` subscribes MQTT and converts the available data for the dtsu666emulator emulator.

## Background:
I have a Growatt SPH photovoltaik inverter, which expects an dtsu666 smartmeter to be installed in the main fuse box.
This is necessay to know, when to charge the battery, show correct energy flow status,...

However, I have already this information from the smartmeter of the grid provider (see project https://github.com/gskjold/AmsToMqttBridge).
I find it redundant, to have two smartmeter installed, wanted to avoid the cabeling between smart meter and inverter.



This project takes the provided info of the MQTT server, modifies it as needed, emulates the dtsu666 smartmeter to be used by the growatt inverter.
( I don't have per phase Power Factor or Reactive Power information, but I don't care about it, only the total power is relevant for me. )


## Dependency:
 - pymodbus 2.5.3 -- not working with version 3.0
