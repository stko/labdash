#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import can
from  jsonstorage import JsonStorage
from datetime import datetime

'''Wrapper function to capsulate the real available can interfaces from a generic bus abbitration to make the scripts independent from the real existing hardware

'''

def LDCANListen(ldm_instance,port=0, bitrate=500000):
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


	

def id_exists(received_msgs_dict : dict, can_id : int, can_mask: int):
      """checks if a (masked) id was received

      :param dict received_msgs_dict: dict of received messages
      :param int can_id: id to search for
      :param int can_mask: if id && can_mask == can_id then True

      :return: True if ID is found
      :rtype: bool

      .. todo::

      """

      if not can_mask:
            return can_id in received_msgs_dict
      else:
            for recv_id in received_msgs_dict:
                  if recv_id & can_mask == can_id:
                        return True
      return False

def rcv_collect( bus, can_ids,timeout, extended, append =False):
      """collects messages over time

      :param obj sender: can bus
      :param list can_ids: list of can IDs to listen for
      :param bool extended: are the ids extended
      :param bool append: if not set, only the last message of an id is kept
      :type priority: integer or None
      :return: dict of received message
      :rtype: dict

      .. todo::

      """
      
      '''
      
      TODO: Die neuen can_masks müssten noch irgendwie mit in den Filter..
      filters=[ {"can_id": can_id,"can_mask": can_id, "extended": extended} for can_id in can_ids]
      bus.set_filters( filters)'''
      res={}
      CAN_ERR_FLAG = 0x20000000
      error_count= 0
      rx_count=0
      error_precentage_rate = 0
      timeout/=1000 # the input is in ms, but python is measuring in secs, so we have to covert it
      after_recv_time=datetime.now()
      while timeout > 0:
            # record the start time
            before_recv_time=after_recv_time
            message = bus.recv(timeout=timeout)
            if not message: # nothing received in time, so timoeout reached -> end loop
                  break
            if (message.arbitration_id & CAN_ERR_FLAG) == CAN_ERR_FLAG:
                  #print ("Can Error Caught")
                  error_count+= 1
            elif message.is_error_frame:
                  #print ("Finally Error Frame")
                  error_count+= 1
            else:
                  rx_count+=1

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
            if rx_count==0:
                  if error_count:
                        error_precentage_rate=100
                  else:
                        error_precentage_rate=0
            else:
                  error_precentage_rate=int(error_count/rx_count *100)
      return res, error_precentage_rate