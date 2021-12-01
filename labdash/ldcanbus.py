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

def send_can_11b( bus, id,data):
	message = can.Message(arbitration_id=id, is_extended_id=False, data=data)
	bus.send(message)

def rcv_can_11b( bus, can_id,timeout):
	'''
	from the python-can can:
		--filter ...  
		Comma separated filters can be specified for the given
		CAN interface: <can_id>:<can_mask> (matches when
		<received_can_id> & mask == can_id & mask)
		<can_id>~<can_mask> (matches when <received_can_id> &
		mask != can_id & mask)
	'''
	return rcv_can( bus, can_id,timeout, False)


def rcv_can_29b( bus, can_id,timeout):
	return rcv_can( bus, can_id,timeout, True)


def rcv_can( bus, can_id,timeout, extended):
	bus.set_filters( [{"can_id": can_id,"can_mask": can_id, "extended": extended}])
	message = bus.recv(timeout=timeout)
	return message

def format_msgs(data, format_str):
	[data_type, bit_pos, bit_len, mult, div, offset,unit] = format_str.split(':')
	bit_pos=int(bit_pos)
	bit_len=int(bit_len)
	mult=float(mult)
	div=float(div)
	offset=float(offset)
	if data_type=='f':
		return str(int.from_bytes(data[bit_pos//8:bit_pos//8+bit_len//8], byteorder='big', signed=False)*mult/div+offset)
	else:
		return 'unknown data type in format_str'

def receive_msg(bus,id,extended):
	if not bus:
		return "Bus Error"
	[can_id_string, timeout, format_str] =id.split(':',2)
	can_id=int(can_id_string,16)
	timeout=int(timeout)/1000
	message=rcv_can(bus,can_id,timeout,extended)
	if not message:
		return '-'
	return format_msgs(message.data,format_str)


	

