#!/usr/bin/python3
# -*- coding: utf-8 -*-
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

import logging
import logging.handlers as Handlers

#log = logging.getLogger("pymodbus.server")
#log.setLevel(logging.DEBUG)

log = logging.getLogger()
log.setLevel(logging.INFO)

from dtsu666emulator import dtsu666Emulator
import paho.mqtt.client as mqtt
import json
import math

RS485Port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.2:1.0-port0' # Smartmeter


MQTT_Settings = {
	"Server":	"10.10.98.71",
	"Port":     	1883,
	"AMS_Topic":	"powermeter",
	}
	
	
	
#--------------------------------------------------
em1 = dtsu666Emulator(
	device=RS485Port
)

em1.startserver()
logging.info('smartmeter started...')


#============================================================================

# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect(client, userdata, flags, rc):
	logging.info(f"MQTT connected with result code {rc}")

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe(MQTT_Settings['AMS_Topic']+"/#")


# The callback for when a PUBLISH message is received from the server.
def mqtt_on_message(client, userdata, msg):
#	print(msg.topic)

	if msg.topic == MQTT_Settings['AMS_Topic']+"/power":
		d = json.loads(msg.payload.decode("utf-8"))

		P = d['P'] - d['PO']
		S = P / d["PF"]
		Q = math.sqrt(S**2 - P**2)

		U1 = (d['U1'] + d['U2'] + d['U3'])/3

		w3 = 1.732050808 # sqrt(3)
		Vab = U1*w3
		
		I = P / (U1 * d["PF"] * 3)

		Inverterdata = {
			# Cosinussatz: sqrt(a² + b² -2*a*b*cos(120°) )
			# -2*cos(120°) = 1

#			'Volts_AB':		math.sqrt( U1**2 + U2**2 + U1*U2),

			'Volts_AB':		Vab,
			'Volts_BC':		Vab,
			'Volts_CA':		Vab,

			'Volts_L1':		U1,
			'Volts_L2':		U1,
			'Volts_L3':		U1,
#			'Current_L1':		d['I1'],
#			'Current_L2':		d['I2'],
#			'Current_L3':		d['I3'],

			'Current_L1':		I,
			'Current_L2':		I,
			'Current_L3':		I,
			
			'Active_Power_L1':	P/3,
			'Active_Power_L2':	P/3,
			'Active_Power_L3':	P/3,

			'Total_System_Power_Factor':	d['PF'],
			'Power_Factor_L1':	d['PF'],	 # don't have the data aund don't care
			'Power_Factor_L2':	d['PF'],
			'Power_Factor_L3':	d['PF'],

			'Reactive_Power_L1':	Q/3,
			'Reactive_Power_L2':	Q/3,
			'Reactive_Power_L3':	Q/3,

			'Total_System_Active_Power':	P,
	#		'Total_System_Apparent_Power':	Pn,
			'Total_System_Reactive_Power':	Q,
			'DmPt': P,

			"Frequency":	50,
			}


		logging.info("..update power..")
		logging.info(pp.pformat(Inverterdata))
		em1.update(Inverterdata)


	elif msg.topic == MQTT_Settings['AMS_Topic']+"/energy":
		d = json.loads(msg.payload.decode("utf-8"))

		Inverterdata = {
			'Total_import_kwh':	d['tPI'],
			'Total_export_kwh':	d['tPO'],
			}

		logging.info("..update energy..")
		em1.update(Inverterdata)


# ========================================================================================================================
mqttclient=mqtt.Client()
mqttclient.on_connect = mqtt_on_connect
mqttclient.on_message = mqtt_on_message
mqttclient.connect(MQTT_Settings['Server'], MQTT_Settings['Port'], 60)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a manual interface.
mqttclient.loop_forever()



