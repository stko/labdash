#!/usr/bin/env python
# -*- coding: utf-8 -*-


import can
from jsonstorage import JsonStorage
from datetime import datetime
import threading

"""Wrapper function to capsulate the real available can interfaces from a generic bus abbitration to make the scripts independent from the real existing hardware

"""

received_msgs={}
error_precentage_rate=0
stop_event=threading.Event()
thread=None
bus=None

def LDCANListen(ldm_instance, port=0, bitrate=500000):
    # reads the config, if any
    global bus, thread

    config = JsonStorage(
        "LDCANBus",
        "backup",
        "config.json",
        {
            "canports": [
                {
                    "bustype": "pcan",
                    "interface": "peak",
                    "channel": "PCAN_USBBUS1",
                },
            ]
        },
    )
    try:
        canports = config.read("canports")
        bus = can.interface.Bus(
            bustype=canports[port]["bustype"],
            channel=canports[port]["channel"],
            bitrate=bitrate,
        )
        ldm_instance.add_close_handler(shutdown)
        global thread
        thread= threading.Thread(target=rcv_listen, args=(bus,))
        print("init thread")
        stop_event.clear()
        thread.start()
        return bus
    except Exception as ex:
        print("Error:", str(ex))
        return None



def id_exists(received_msgs_dict: dict, can_id: int, can_mask: int):
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


def rcv_listen(bus, can_ids =None, timeout=0.1, extended=False, append=False):
      """Thread which collects messages in received_msgs

      :param obj sender: can bus
      :param list can_ids: list of can IDs to listen for  # ACTUAL NOT SUPPORTED
      :param float timeout: wait time for a message
      :param bool extended: are the ids extended  # ACTUAL NOT SUPPORTED
      :param bool append: if not set, only the last message of an id is kept


      .. todo::

      """

      """
      
      TODO: Die neuen can_masks müssten noch irgendwie mit in den Filter..
      filters=[ {"can_id": can_id,"can_mask": can_id, "extended": extended} for can_id in can_ids]
      bus.set_filters( filters)
      """
      global error_precentage_rate
      print("start thread")
      while not stop_event.is_set():
            CAN_ERR_FLAG = 0x20000000
            error_count = 0
            rx_count = 0
            message = bus.recv(timeout=timeout)
            if not message:  # nothing received in time, so timoeout reached -> end loop
                continue
            if (message.arbitration_id & CAN_ERR_FLAG) == CAN_ERR_FLAG:
                # print ("Can Error Caught")
                error_count += 1
            elif message.is_error_frame:
                # print ("Finally Error Frame")
                error_count += 1
            else:
                rx_count += 1
            if append:
                if not message.arbitration_id in received_msgs:
                        received_msgs[message.arbitration_id] = [message]
                else:
                        received_msgs[message.arbitration_id].append(message)
            else:
                received_msgs[message.arbitration_id] = [message]
            if rx_count == 0:
                if error_count:
                        error_precentage_rate = 100
                else:
                        error_precentage_rate = 0
            else:
                error_precentage_rate = int(error_count / rx_count * 100)


def rcv_collect():
     return received_msgs


def shutdown():
      if thread:
            stop_event.set()
            thread.join()
      if bus:
            bus.shutdown()

