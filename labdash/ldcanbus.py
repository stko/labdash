#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import can
#from uds import Uds
from  jsonstorage import JsonStorage
from datetime import datetime
import traceback

import can
import can.interfaces.pcan


'''Wrapper function to capsulate the real available can interfaces from a generic bus abbitration to make the scripts independent from the real existing hardware

'''

def LDCANBus(ldm_instance,port=0, bitrate=500000):
	# reads the config, if any
	config = JsonStorage('LDCANBus', 'backup', "config.json",
		{
			'canports' :
			[
				{
					"bustype": "pcan",
					"interface": "peak",
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

'''Wrapper function to bind the UDS connection to the lccan settings

IMPORTANT: To make this work, the can-uds python library need to patched! :
https://github.com/stko/python-uds/commit/00878336be1be6bffc4a5e5f083f8ed72580e850

'''


'''
def LDUDS(ldm_instance, port=0, bitrate=500000, resId=0x7E0, reqId=0x7E8):
	# reads the config, if any
	config = JsonStorage('LDCANBus', 'backup', "config.json",
		{
			'canports' :
			[
				{
					"bustype": "pcan",
					"interface": "peak",
					"channel": "PCAN_USBBUS1",
				},
			]

		})
	try:
		canports=config.read('canports')
		uds = Uds (resId=resId, reqId=reqId, transportProtocol="CAN", baudrate= bitrate, interface=canports[port]['interface'], device=canports[port]['channel'])

		ldm_instance.add_close_handler(uds.disconnect)
		return uds
	except Exception as ex:
		print('Error:', str(ex))
		return None

'''
def send_can_11b( bus, id,data):
	message = can.Message(arbitration_id=id, is_extended_id=False, data=data)
	bus.send(message)

def send_can_29b( bus, id,data):
	message = can.Message(arbitration_id=id, is_extended_id=True, data=data)
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


def rcv_can( bus, can_id,timeout, extended ):
	bus.set_filters( [{"can_id": can_id,"can_mask": can_id, "extended": extended}])
	message = bus.recv(timeout=timeout)
	return message

def rcv_collect( bus, can_ids,timeout, extended, append =False):
	filters=[ {"can_id": can_id,"can_mask": can_id, "extended": extended} for can_id in can_ids]
	bus.set_filters( filters)
	res={}
	timeout/=1000 # the input is in ms, but python is measuring in secs, so we have to covert it
	after_recv_time=datetime.now()
	while timeout > 0:
		# record the start time
		before_recv_time=after_recv_time
		message = bus.recv(timeout=timeout)
		if not message: # nothing received in time, so timoeout reached -> end loop
			break
		# take the finishing time
		after_recv_time=datetime.now()
		# calculate the time is has taken for the last recv
		time_d_float = (after_recv_time - before_recv_time ).total_seconds()
		# substract the time taken from the total timeout
		timeout -=time_d_float
		if append:
			if not message.arbitration_id in res:
				res[message.arbitration_id]=[message]
			else:
				res[message.arbitration_id].append(message)
		else:
			res[message.arbitration_id]=[message]
	return res

def receive_msg(bus,id,extended):
	if not bus:
		return "Bus Error"
	[can_id_string, timeout, format_str] =id.split(':',2)
	can_id=int(can_id_string,16)
	timeout=int(timeout)/1000
	message=rcv_can(bus,can_id,timeout,extended)
	return message


	

