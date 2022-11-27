#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import logging

from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.version import version as ModbusVersion
from pymodbus.constants import Endian

#from pymodbus.server import StartSerialServer
#from pymodbus.server.async import StartSerialServer
from pymodbus.server.sync import StartSerialServer

from pymodbus.transaction import ModbusRtuFramer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from threading import Thread

wordorder = Endian.Big
byteorder = Endian.Big

header = [207, 701, 0, 0, 0, 0, 1, 10, 0, 0, 0, 1, 0, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 1, 10, 0, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 0, 0, 0, 0, 3, 3, 4]

Registermapping = {
	"Volts_AB":	{"addr":0x2000, 'scale': .1},
	"Volts_BC":	{"addr":0x2002, 'scale': .1},
	"Volts_CA":	{"addr":0x2004, 'scale': .1},
	"Volts_L1":	{"addr":0x2006, 'scale': .1},
	"Volts_L2":	{"addr":0x2008, 'scale': .1},
	"Volts_L3":	{"addr":0x200A, 'scale': .1},
	"Current_L1":	{"addr":0x200C, 'scale': .001},
	"Current_L2":	{"addr":0x200E, 'scale': .001},
	"Current_L3":	{"addr":0x2010, 'scale': .001},
	"Active_Power_L1":	{"addr":0x2014, 'scale': .1},
	"Active_Power_L2":	{"addr":0x2016, 'scale': .1},
	"Active_Power_L3":	{"addr":0x2018, 'scale': .1},
	"Reactive_Power_L1":	{"addr":0x201C, 'scale': .1},
	"Reactive_Power_L2":	{"addr":0x201E, 'scale': .1},
	"Reactive_Power_L3":	{"addr":0x2020, 'scale': .1},
	"Power_Factor_L1":	{"addr":0x202C, 'scale': .001},
	"Power_Factor_L2":	{"addr":0x202E, 'scale': .001},
	"Power_Factor_L3":	{"addr":0x2030, 'scale': .001},
	"Total_System_Active_Power":	{"addr":0x2012, 'scale': .1},
	"Total_System_Reactive_Power":	{"addr":0x201A, 'scale': .1},
	"Total_System_Power_Factor":	{"addr":0x202A, 'scale': .001},
	"Frequency":					{"addr":0x2044, 'scale': .01},
	"DmPt":							{"addr":0x2050, 'scale': .1},
	"Total_import_kwh":	{"addr":0x401E, 'scale': 1},
	"Total_export_kwh":	{"addr":0x4028, 'scale': 1},
#	"Total_Q1_kvarh":	{"addr":0x4032, 'scale': 1000},
#	"Total_Q2_kvarh":	{"addr":0x403C, 'scale': 1000},
#	"Total_Q3_kvarh":	{"addr":0x4046, 'scale': 1000},
#	"Total_Q4_kvarh":	{"addr":0x4050, 'scale': 1000},
}

class dtsu666Emulator:
	def __init__(self, 
		device,
		SlaveID=0x04
		):
		
		self.threads = {}

		# ----------------------------------------------------------------------- #
		# initialize the server information
		i1 = ModbusDeviceIdentification()
		i1.VendorName = 'Pymodbus'
		i1.ProductCode = 'PM'
		i1.VendorUrl = 'http://github.com/riptideio/pymodbus/'
		i1.ProductName = 'Pymodbus Server'
		i1.ModelName = 'Pymodbus Server'
#		i1.MajorMinorRevision = '1.5'
		i1.MajorMinorRevision = ModbusVersion.short()


#		self.RS485Port=device
		self.RS485Settings = {
			'port': device, 
			'baudrate': 9600, 
			'timeout': 0.005, 
			'stopbits': 1, 
			'bytesize': 8, 
			'parity': 'N',
#			'identity': i1
			}


		self.block = ModbusSequentialDataBlock(0, [0]*0x4052)
		# Add header:
		self._setval(0, header)

		self.store   = ModbusSlaveContext(hr=self.block)
		self.context = ModbusServerContext(slaves={SlaveID: self.store}, single=False)

	#------------------------------------------------
	def _setval(self, addr, data):
		self.block.setValues((addr+1), data)	# why +1 ?! ..ugly

	#------------------------------------------------
	def _startserver(self):
		srv = StartSerialServer(context=self.context, framer=ModbusRtuFramer, **self.RS485Settings)

		logging.info('Modbus server started')

	#------------------------------------------------
	def _datejob(self):
		while True:
			self.set_date()
			time.sleep(1)

	#------------------------------------------------
	def startserver(self):
		self.threads['srv'] = Thread(target=self._startserver)
		self.threads['srv'].start()

		self.threads['date'] = Thread(target=self._datejob)
		self.threads['date'].start()

	#------------------------------------------------
	def set_date(self):
		now = datetime.datetime.now()
		builder = BinaryPayloadBuilder(byteorder=byteorder, wordorder=wordorder)
		builder.add_16bit_int(now.second)
		builder.add_16bit_int(now.minute)
		builder.add_16bit_int(now.hour)
		builder.add_16bit_int(now.day)
		builder.add_16bit_int(now.month)
		builder.add_16bit_int(now.year)

		self._setval(0x002f, builder.to_registers())

	#------------------------------------------------
	def update(self, data):
		for k,v in data.items():
			reg = Registermapping[k]["addr"]

			d = v / Registermapping[k]["scale"]
			builder = BinaryPayloadBuilder(byteorder=byteorder, wordorder=wordorder)
			builder.add_32bit_float(d)

			self._setval(reg, builder.to_registers())

# ==========================================================================================
# ==========================================================================================
if __name__ == "__main__":

	#RS485Port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.1.2:1.0-port0' # Smartmeter
	RS485Port = "/dev/pts/7"

	em1 = dtsu666Emulator(
		device=RS485Port
	)

	em1.startserver()

	Testdata = {'Volts_AB': 403.6, 'Volts_BC': 408.0, 'Volts_CA': 404.5, 'Volts_L1': 231.0, 'Volts_L2': 235.1, 'Volts_L3': 236.1, 'Current_L1': 0.339, 'Current_L2': 0.36, 'Current_L3': 0.352, 'Active_Power_L1': 2.8, 'Active_Power_L2': 11.8, 'Active_Power_L3': 8.5, 'Reactive_Power_L1': -76.7, 'Reactive_Power_L2': -80.0, 'Reactive_Power_L3': -79.7, 'Power_Factor_L1': 0.036, 'Power_Factor_L2': 0.14, 'Power_Factor_L3': 0.102, 'Total_System_Active_Power': 23.2, 'Total_System_Reactive_Power': -236.5, 'Total_System_Power_Factor': 0.094,}


	while True:
		logging.info("updating the context")
		em1.update(Testdata)
		time.sleep(10)

	print("bla")


