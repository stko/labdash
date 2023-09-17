#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import can
from jsonstorage import JsonStorage
from datetime import datetime
import threading
import queue

import isotp_listener

"""Wrapper function to capsulate the real available can interfaces from a generic bus abbitration to make the scripts independent from the real existing hardware

"""

received_msgs = {}
error_precentage_rate = 0
stop_event = threading.Event()
thread = None
bus = None

challenge_response_protocol_queue = queue.Queue()
challenge_response_protocols={}

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
        thread = threading.Thread(target=rcv_listen, args=(bus,))
        print("init thread")
        stop_event.clear()
        thread.start()
        return bus
    except Exception as ex:
        print("Error:", str(ex))
        return None

def configure_challenge_response_protocol(name: str, options: object=None):
    """adds challenge response protocol handlers, returns or modifies the actual options

    :param str name: the name (not dynamic yet, must be hardcoded available)
    :param obj options: handler specific set of options. If None, the function returns the actual option set

    :return obj options: if input options are None, the function returns the actual option set
      """    
    if options:
        if name not in challenge_response_protocols:
            if name=="isotp":
                challenge_response_protocols[name]={
                    "protocol":isotp_listener.Isotp_Listener(options),
                    "queue": queue.Queue(),
                    "busy":False
                    }
                return
            print(f"ERROR: {name} is an unknown challenge response protocol")
        else:
            challenge_response_protocols[name]["protocol"].update_options(options)
    else:
        if name not in challenge_response_protocols:
            print(f"ERROR: {name} is an unknown challenge response protocol")
            return None
        else:
            return challenge_response_protocols[name]["protocol"].get_options()

# callback function for istotp_listener to allow to send own can messages
def msg_send(can_id : int, data :bytearray,len: int, is_extended=False):
    try:
        msg = can.Message(arbitration_id=can_id, data=data[:len], is_extended_id=False)
        bus.send(msg)
        return 0
    except:
        print("Can't write to socket")
        return 1

def uds_handler(request_type: isotp_listener.RequestType,  receive_buffer:isotp_listener.uds_buffer,  receive_len : int,  send_buffer : isotp_listener.uds_buffer):
    send_len=0
    print("receive")
    if request_type == isotp_listener.RequestType.Service:
        name="isotp"
        if name not in challenge_response_protocols:
            print(f"ERROR: {name} is an unknown challenge response protocol")
            return send_len
        busy=challenge_response_protocols[name]["busy"]
        queue=challenge_response_protocols[name]["queue"]
        if busy:
            queue.put({"type":"data","data":receive_buffer,"len":receive_len})

    return send_len; # something went wrong, we should never be here..

def send_ticks():
    '''
    send the timer tick to the C&R handlers
    '''
    for challenge_response_protocol in challenge_response_protocols.values():
        protocol=challenge_response_protocol["protocol"]
        queue=challenge_response_protocol["queue"]
        busy=challenge_response_protocol["busy"]

        if challenge_response_protocol["protocol"].tick(time.time()) and busy:
            queue.put({"type":"timeout"})
        else:
            if busy:
                queue.put({"type":"wait"})

def challenge_response_request(name:str, data : bytearray):
    if name not in challenge_response_protocols:
        print(f"ERROR: {name} is an unknown challenge response protocol")
        return None
    protocol=challenge_response_protocols[name]["protocol"]
    if protocol.busy():
        return {"error": "protocol busy", "data": None}
    queue=challenge_response_protocols[name]["queue"]
    with queue.mutex:
        queue.queue.clear()
    challenge_response_protocols[name]["busy"]=True
    protocol.send_telegram(data,len(data))
    while True:
        q=queue.get(timeout=0.1)
        if not q: # something is broken :-(
            print("broken queue")
            challenge_response_protocols[name]["busy"]=False
            return {"error": "queue timeout", "data": None}
        if q["type"]=="wait":
            #print("wait")
            time.sleep(0.01)
            continue
        if q["type"]=="timeout":
            print("timeout queue")
            challenge_response_protocols[name]["busy"]=False
            return {"error": "answer timeout", "data": None}
        if q["type"]=="data":
            print("data queue")
            challenge_response_protocols[name]["busy"]=False
            buffer = bytearray(isotp_listener.UDS_BUFFER_SIZE) # generate a copy of the data
            buffer[:q["len"]] = q["data"]
            nr_of_bytes=q["len"]
            return {"error": "", "data": buffer,"len":nr_of_bytes}
   

def forward_to_protocols(can_id : int, data : bytearray, nr_of_bytes: int):
    for challenge_response_protocol in challenge_response_protocols.values():
        protocol=challenge_response_protocol["protocol"]
        protocol.eval_msg( can_id , data , nr_of_bytes)

def rcv_listen(bus, can_ids=None, timeout=0.01, extended=False, collect_time=0):
    """Thread which collects messages in received_msgs

    :param obj sender: can bus
    :param list can_ids: list of can IDs to listen for  # ACTUAL NOT SUPPORTED
    :param float timeout: wait time for a message
    :param bool extended: are the ids extended  # ACTUAL NOT SUPPORTED
    :param float collect_time: collect time in secs: if 0, only the last message of an id is kept,
        otherways the messages over the collect time


    .. todo::
        Die neuen can_masks müssten noch irgendwie mit in den Filter..
        filters=[ {"can_id": can_id,"can_mask": can_id, "extended": extended} for can_id in can_ids]
        bus.set_filters( filters)
      """
    # initialize protocols
    # prepare the options for uds_listener
    options = isotp_listener.IsoTpOptions()
    options.target_address = 0x7E1 # uds answer address
    options.source_address = options.target_address | 8 # listen on can ID 
    options.bs=10 # The block size sent in the flow control message. Indicates the number of consecutive frame a sender can send before the socket sends a new flow control. A block size of 0 means that no additional flow control message will be sent (block size of infinity)
    options.stmin =5 # time to wait
    options.send_frame = msg_send # assign callback function to allow isotp_listener to send messages
    options.uds_handler = uds_handler # assign callback function to allow isotp_listener to announce incoming requests
    configure_challenge_response_protocol("isotp",options)
    global error_precentage_rate
    print("start receive thread")
    while not stop_event.is_set():
        CAN_ERR_FLAG = 0x20000000
        error_count = 0
        rx_count = 0
        message = bus.recv(timeout=timeout)
        if not message:  # nothing received in time, so timoeout reached -> end loop
            send_ticks()
            continue
        if (message.arbitration_id & CAN_ERR_FLAG) == CAN_ERR_FLAG:
            # print ("Can Error Caught")
            error_count += 1
        elif message.is_error_frame:
            # print ("Finally Error Frame")
            error_count += 1
        else:
            rx_count += 1
        forward_to_protocols(message.arbitration_id,message.data,message.dlc)
        this_time = time.time()
        if collect_time:
            max_age = this_time - collect_time
            if not message.arbitration_id in received_msgs:
                received_msgs[message.arbitration_id] = [
                    {"timestamp": this_time, "msg": message}
                ]
            else:
                received_msgs[message.arbitration_id].append(
                    {"timestamp": this_time, "msg": message}
                )
            # remove old msgs
            for msgs in received_msgs.values():
                for msg in msgs[
                    :
                ]:  # this generates a copy of msgs to allow deleting while looping
                    if msg["timestamp"] < max_age:
                        received_msgs.remove(msg)
        else:
            received_msgs[message.arbitration_id] = [
                {"timestamp": this_time, "msg": message}
            ]
        if rx_count == 0:
            if error_count:
                error_precentage_rate = 100
            else:
                error_precentage_rate = 0
        else:
            error_precentage_rate = int(error_count / rx_count * 100)
    print("end receive thread")


def rcv_collect(can_id: int, can_mask: int = 0, age_ms: int = 0):
    """
    :param int can_id: can id to filter for
    :param int can_mask: if set, used as mask to filter for can ids. (received_id & can_mask == can_id)
    :param float age_ms: if set as ms, only the msgs are returned which are not older as age

    :return list: list of all collected msg IDs and its message
    """
    result = {}
    act_timestamp = time.time() - float(age_ms / 1000)
    for id, msgs in received_msgs.items():
        if not can_mask:
            if can_id != id:
                continue
        else:
            if id & can_mask != can_id:
                continue
        for msg_data in msgs:
            if age_ms == 0 or msg_data["timestamp"] >= act_timestamp:
                if id not in result:
                    result[id] = [msg_data["msg"]]
                else:
                    result[id].append(msg_data["msg"])
    return result


def shutdown():
    if thread:
        stop_event.set()
        thread.join()
    if bus:
        bus.shutdown()
