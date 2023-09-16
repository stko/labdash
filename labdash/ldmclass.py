#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import threading
import time
from abc import ABCMeta, abstractmethod
import defaults
import traceback
from bitstring import BitArray  # nice module for bit wise operations


class LDMClass(metaclass=ABCMeta):
    """Partly abstract class as base class for LabDash modules"""

    # Visualizer flag constants
    VI_SUBMENU = 1  # visible indication of a submeni, no function
    VI_UPDATE = 2  # gets updated when the update button is pressed
    VI_TIMER = 4  # gets updated when the update timer is running
    VI_LOG = 8  # writes an entry in the text output, whenever the value changes
    VI_BACK = 16  # would be called if on the UI the hard coded "Back"- button is used (only in hard coded UIs, not (yet) in Browser)
    VI_GRAPH = 32  # ???

    def __init__(self, msg_handler):
        self.msg_handler = msg_handler
        self.closeHandlers = set()
        self.bus = None
        self.answer_handler = None

    def add_close_handler(self, close_handler):
        self.closeHandlers.add(close_handler)

    def event_listener(self, queue_event):
        """handler for system events"""
        print("LDMClass event handler", queue_event.type, queue_event.user)

        if queue_event.type == defaults.MSG_SOCKET_BROWSER:
            print("Message from Browser")
            data = queue_event.data
            if "name" in data and "actValue" in data and "updType" in data:  # a
                name = data["name"]
                actValue = data["actValue"]
                updType = data["updType"]
                try:
                    new_Value = self.execute_method_by_name(name, actValue, updType)
                    self.msg_handler.queue_event(
                        None,
                        defaults.MSG_SOCKET_MSG,
                        {
                            "type": defaults.CM_VALUE,
                            "config": {"to": {"name": name}, "value": new_Value},
                        },
                    )
                except Exception as ex:
                    print("Error: Execption when execute script function", str(ex))

                return None  # event handled, no further processing
            if "type" in data and data["type"] == "PARAM" and "answer" in data:  # a
                if self.answer_handler:
                    self.answer_handler(data["answer"])
                    self.answer_handler = None

        return queue_event

    def query_handler(self, queue_event, max_result_count):
        """handler for system queries"""
        pass

    def run(self):
        """starts the child thread"""
        """  #### first we try without being a thread
		# Create a Thread with a function without any arguments
		#th = threading.Thread(target=_ws_main, args=(server,))
		self.th = threading.Thread(target=self.child._run)
		# Start the thread
		self.th.setDaemon(True)
		self.th.start()
		"""
        self.execute_method_by_name("main", None, None)

    def stop(self, timeout=0):
        """stops the child thread. If timeout > 0, it will wait timeout secs for the thread to finish"""
        """  #### first we try without being a thread
		self.child._stop()
		if timeout > 0:
			self.th.join(timeout)
		return self.th.isAlive()
		"""
        for handler in self.closeHandlers:
            print("close handler")
            handler()  # call all close handlers

    def execute_method_by_name(self, name, oldvalue, updType):
        try:
            elements = name.split(":", 1)  # seperate function name from optId
            if len(elements) > 1:
                name = elements[0]
                id = elements[1]
            else:
                id = ""
            return getattr(self, name)(oldvalue, id)
        except Exception as e:
            print(f"Can't execute method {name} " + str(e))
            traceback.print_exc(file=sys.stdout)

    # some convience methods
    def format_msgs(self, data_bytes, format_str):
        """
        format types:
        a: ASCII
        f: float
        e: enum : The calculated value is used as index for the different texts which are stored in the Unit field, seperated by &
        b: binary

        all formats are also exist as j.. (ja, jf..), where the leading j indicates that the data type is j1939, which has special
        formats, ranges and error indications

        """
        if not data_bytes:
            return "-"
        [data_type, bit_pos, bit_len, mult, div, offset, unit] = format_str.split(":",6)
        bit_pos = int(bit_pos)
        bit_len = int(bit_len)
        mult = float(mult)
        div = float(div)
        offset = float(offset)
        # length check
        if data_type != "a":
            if bit_pos // 8 + bit_len // 8 > len(data_bytes):
                return "message data too short",0
        # test, if we can use faster byte oriented methods or bit-wise, but slower bitstring operations
        if bit_pos % 8 == 0 and bit_len % 8 == 0:
            message_data_bytes = data_bytes[bit_pos // 8 : bit_pos // 8 + bit_len // 8]
        else:
            message_data_bytes = BitArray(data_bytes)
            print(str(message_data_bytes.b))
            message_data_bytes = message_data_bytes[bit_pos : bit_pos + bit_len]
            if bit_len % 8 != 0:  # we need to do padding :-(
                # first we need the numpber of leading padding bits
                padding_string = "0b" + "0" * (8 - (bit_len % 8))
                padding_bits = BitArray(padding_string)
                padding_bits.append(message_data_bytes)
                message_data_bytes = padding_bits.tobytes()
            else:
                message_data_bytes = message_data_bytes.tobytes()

        if data_type == "f":
            raw = (
                int.from_bytes(message_data_bytes, byteorder="big", signed=False)
                * mult
                / div
                + offset
            )
            return str(raw) + unit, raw
        if data_type == "b":
            raw = message_data_bytes !=  b'\x00'
            values = unit.split("&")
            if raw:
                value = values[1]
            else:
                value = values[0]
            return value, raw
        if data_type == "a":
            bytearray_message = bytearray(message_data_bytes)
            return bytearray_message.decode("utf-8"), bytearray_message
        return "unknown data type in format_str", None

    # implementation of the old OOBD lua interface commands

    def openPage(self, name):
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {"type": defaults.CM_PAGE, "config": {"name": name}},
        )

    def addElement(
        self, tooltip, name, value, oobdElementFlags=None, optid=None, optTable=None
    ):
        msg = {
            "tooltip": tooltip,
            "name": name,
            "value": value,
        }
        if oobdElementFlags:
            msg["updevents"] = oobdElementFlags
        if optid:
            msg["name"] += ":" + optid
        if optTable:
            msg["opts"] = optTable
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {"type": defaults.CM_VISUALIZE, "config": msg},
        )

    def pageDone(self):
        self.msg_handler.queue_event(
            None, defaults.MSG_SOCKET_MSG, {"type": defaults.CM_PAGEDONE, "config": {}}
        )

    def openXCVehicleData(*args, **kwargs):
        print("Warning: Call of non implemented legacy function xx()")

    def serReadLn(*args, **kwargs):
        print("Warning: Call of non implemented legacy function xx()")

    def serWait(*args, **kwargs):
        print("Warning: Call of non implemented legacy function xx()")

    def serSleep(delay):
        time.sleep(delay)

    def serWrite(*args, **kwargs):
        print("Warning: Call of non implemented legacy function xx()")

    def serFlush(*args, **kwargs):
        print("Warning: Call of non implemented legacy function xx()")

    def displayWrite(self, text, cmd=None):
        msg = {
            "command": "serDisplayWrite",
            "data": text,
        }
        if cmd:
            msg["modifier"] = cmd
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {"type": defaults.MSG_SOCKET_WRITESTRING, "config": msg},
        )

    def msgBox(self, typeOfBox, title, text, handler, default="OK"):
        self.answer_handler = handler
        typeOfBox = typeOfBox.lower()
        if typeOfBox == "alert":
            self.msg_handler.queue_event(
                None,
                defaults.MSG_SOCKET_MSG,
                {
                    "type": defaults.CM_DIALOG_INFO,
                    "config": {"DIALOG_INFO": {"title": title, "tooltip": text}},
                },
            )
            return
        msg = {
            defaults.CM_PARAM: {
                "type": "String",
                "title": title,
                "text": text,
                "default": default,
            }
        }
        if typeOfBox == "confirm":
            msg["confirm"] = "yes"

        self.msg_handler.queue_event(
            None, defaults.MSG_SOCKET_MSG, {"type": defaults.CM_PARAM, "config": msg}
        )
        print("Warning: Waiting for answer in msgBox() not correctly implemented yet")

    def onionMsg(*args, **kwargs):
        print("Warning: Call of non implemented legacy function onionMsg()")

    def dbLookup(*args, **kwargs):
        print("Warning: Call of non implemented legacy function dbLookup()")

    def ioInput(*args, **kwargs):
        print("Warning: Call of non implemented legacy function ioInput()")

    def ioRead(*args, **kwargs):
        print("Warning: Call of non implemented legacy function ioRead()")

    ##### new commands  ##
    def send_value(self, name, new_Value):
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {
                "type": defaults.CM_VALUE,
                "config": {"to": {"name": name}, "value": new_Value},
            },
        )
