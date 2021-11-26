#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import can
from  jsonstorage import JsonStorage
import defaults
import traceback

import can
import can.interfaces.pcan


'''Wrapper function to capsulate the real available can interfaces from a generic bus abbitration to make the scripts independent from the real existing hardware

'''

def LDCANBus(ldm_instance,port=0, bitrate=500000):
	# reads the config, if any
	config = JsonStorage('Interfaces', 'backup', "config.json",
		{
			'canports' :
			[
				{
					"bustype": "pcan",
					"channel": "PCAN_USBBUS1",
				},
			]

		})
	try:
		canports=config.read('canports')
		bus= can.interface.Bus(bustype=canports[port]['bustype'], channel=canports[port]['channel'], bitrate=bitrate)
		ldm_instance.add_close_handler(bus.shutdown)
		return bus
	except Exception as ex:
		print('Error:', str(ex))
		return None

