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
from utils.byteformatter import format_msgs
import oyaml


class EOLClass(metaclass=ABCMeta):
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

            if "type" in data:
                # forwards the answer from a dialog to an answer handler
                if data["type"] == "PARAM" and "answer" in data:  # a
                    if self.answer_handler:
                        self.answer_handler(data["answer"])
                        self.answer_handler = None

                # Starts the "Run" Process
                if data["type"] == "PLAYREQUEST":
                    print(data)
                    self.setStatusIcons({"4711": "OK"})

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
    def format_msgs(self, data_bytes, id):
        return format_msgs(data_bytes,id)

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

    def eollist(self, title, items):
        msg = {"title": title, "items": items}
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {"type": defaults.CM_EOL_EOLLIST, "config": msg},
        )

    def setStatusIcons(self, states):
        msg = {"states": states}
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {"type": defaults.CM_EOL_ICONSTATES, "config": states},
        )
    def load_procedures(self,file_path="procedures.yaml"):
        '''
        load the procedures definition files
        '''
        try:
            with open(file_path,encoding="utf-8") as fin:
                procedure= oyaml.load_all(fin)
        except oyaml.YAMLError as exc:
            return exc
        