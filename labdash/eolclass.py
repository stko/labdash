#!/usr/bin/env python
# -*- coding: utf-8 -*-


import importlib
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


class TestResult:
    """
    little helper class to handle the outcome of a test
    """

    not_tested = 1

    def __init__(self):
        self.state = self.not_tested


class EOLClass(metaclass=ABCMeta):
    """Partly abstract class as base class for LabDash modules"""

    # Visualizer flag constants
    VI_SUBMENU = 1  # visible indication of a submeni, no function
    VI_UPDATE = 2  # gets updated when the update button is pressed
    VI_TIMER = 4  # gets updated when the update timer is running
    VI_LOG = 8  # writes an entry in the text output, whenever the value changes
    VI_BACK = 16  # would be called if on the UI the hard coded "Back"- button is used (only in hard coded UIs, not (yet) in Browser)
    VI_GRAPH = 32  # ???

    def __init__(self, msg_handler, full_path_name: str, module_dirs: list):
        self.msg_handler = msg_handler
        self.full_path_name = full_path_name
        self.module_dirs = module_dirs
        self.closeHandlers = set()
        self.test_units = {}
        self.module_paths = {}
        self.bus = None
        self.answer_handler = None
        self.is_running = False  # a flag to exit the execution loop, when running
        self.waiting_for_answer = (
            False  # a flag to exit the execution loop, when running
        )

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
        return format_msgs(data_bytes, id)

    def displayWrite(self, text, cmd=None):
        if not self.msg_handler:  # if the EOLClass was started standalone
            return
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
        if not self.msg_handler:  # if the EOLClass was started standalone
            return
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
        if not self.msg_handler:  # if the EOLClass was started standalone
            return
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {
                "type": defaults.CM_VALUE,
                "config": {"to": {"name": name}, "value": new_Value},
            },
        )

    def eollist(self, title, items):
        if not self.msg_handler:  # if the EOLClass was started standalone
            return
        msg = {"title": title, "items": items}
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {"type": defaults.CM_EOL_EOLLIST, "config": msg},
        )

    def setStatusIcons(self, states):
        if not self.msg_handler:  # if the EOLClass was started standalone
            return
        msg = {"states": states}
        self.msg_handler.queue_event(
            None,
            defaults.MSG_SOCKET_MSG,
            {"type": defaults.CM_EOL_ICONSTATES, "config": states},
        )

    def load_procedures(self):
        """
        load the procedures definition files
        """
        ecus_file_path = os.path.join(self.full_path_name, "ECUs.yaml")
        try:
            with open(ecus_file_path, encoding="utf-8") as fin:
                self.ecus = oyaml.load(fin, Loader=oyaml.Loader)["modules"]
        except oyaml.YAMLError as exc:
            self.ecus = {}
        self.test_units = {}
        temporary_test_units = {}
        try:
            for file in os.listdir(self.full_path_name):
                try:
                    if file.endswith(".eoltest.yaml"):
                        unit_name = os.path.basename(file)
                        eoltest_file_path = os.path.join(self.full_path_name, file)
                        with open(eoltest_file_path, encoding="utf-8") as fin:
                            this_unit = oyaml.load(fin, Loader=oyaml.Loader)
                            if "system" in this_unit:
                                unit_name = this_unit["system"]
                            else:
                                unit_name = os.path.basename(file)
                            if unit_name not in temporary_test_units:
                                temporary_test_units[unit_name] = {}
                            temporary_test_units[unit_name].update(this_unit)
                except oyaml.YAMLError as exc:
                    pass
        except Exception as ex:
            print("listdir error", str(ex))
        # as next, preforming the loaded structures in temporary_test_units to their full content

        for unit_name, unit_data in temporary_test_units.items():
            self.test_units[unit_name] = {}
            for test_name, input_test_data in unit_data.items():
                if test_name not in ["system"]:  # filter for unwanted properties
                    test_data = {}
                    # as next we replace dependencies names with fully qualified identifiers
                    for property, property_data in input_test_data.items():
                        if property in ["depends", "repair"]:
                            test_data[property] = []
                            for single_test in property_data:
                                if (
                                    not isinstance(single_test, str)
                                    or ":" in single_test
                                ):  # it's either no dependency (no string) or already qualified
                                    test_data[property].append(single_test)
                                else:
                                    test_data[property].append(
                                        unit_name + ":" + single_test
                                    )

                        else:
                            test_data[property] = property_data
                    self.test_units[unit_name][unit_name + ":" + test_name] = test_data
                    test_data["result"] = TestResult()
        pass

    def get_test_tree(self):
        # first
        pass

    #### the test routines
    def execute_unit(self):
        pass

    def create_module(self, name: str, module_name: str):
        """
        scans all module dirs if the wanted module is in
        """
        instance = None
        if module_name not in self.module_paths:
            full_module_name = "ldm_" + module_name + ".py"
            for dir in self.module_dirs:
                for file_name in os.listdir(dir):
                    if file_name == full_module_name:
                        self.module_paths[module_name] = {
                            "name": full_module_name,
                            "path": os.path.join(dir, full_module_name),
                        }
                        break
        if module_name in self.module_paths:
            module_location = self.module_paths[module_name]

            try:

                module_spec = importlib.util.spec_from_file_location(
                    module_location["name"],
                    module_location["path"],
                    submodule_search_locations=[
                        os.path.dirname(os.path.abspath(__file__))
                    ],
                )
                my_module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(my_module)
                instance = my_module.EOLModule(name)

            except Exception as e:
                print(f"Can't load plugin {module_name}:{str(e)}")
                traceback.print_exc(file=sys.stdout)
        return instance


if __name__ == "__main__":
    print("geht 1")
    eolclass = EOLClass(
        None,
        "/home/steffen/Desktop/workcopies/labdash_internal/modules/",
        ["/home/steffen/Desktop/workcopies/labdash_internal/modules/"],
    )
    print("geht 2")
    mrs = eolclass.create_module("A65", "mrs")
    print("geht 3")
    if mrs:
        print("Wahnsinn!")
    mrs.flash(None)
    print(mrs.name)
