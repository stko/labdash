#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys

from rich.prompt import Confirm
from rich.console import Console
from labdash import eolclass
from labdash.directorymapper import DirectoryMapper


class CLI:
    """
    handle the user inputs
    """

    def __init__(self, module_dir: str):
        self.module_handler = eolclass.EOLClass(
            None,
            module_dir,
            [module_dir],
        )
        self.loaded_module_driver = None
        self.found_modules = {}
        self.console = Console()
        self.end_flag = False
        self.cmds = {
            "quit": {"help": "Quits the program", "f": self.quit},
            "help": {"help": "print this help", "f": self.help},
            "load": {
                "help": "load the given module by its name as current module",
                "f": self.load,
            },
            "scan": {"help": "let the module scan the bus", "f": self.scan},
            "flash": {
                "help": "flashes the firmware defined by the download url parameter",
                "f": self.flash,
            },
            "erase": {"help": "erase the eeprom", "f": self.erase},
            "parametrize": {
                "help": "sends a json parameter file to node id (parameter_file hex_node_id)",
                "f": self.parametrize,
            },
        }
        while not self.end_flag:
            user_input = self.console.input("Your command (enter for help): ")
            if user_input:
                elements = user_input.split()
                choices = []
                for cmd, info in self.cmds.items():
                    if cmd.startswith(elements[0].lower()):
                        choices.append(cmd)
                if len(choices) == 1:
                    info = self.cmds[choices[0]]
                    if info["f"] is not None:
                        info["f"](elements[1:])
                if len(choices) > 1:
                    self.console.print(
                        "Did you meant '"
                        + "', ".join(choices[:-1])
                        + "' or '"
                        + choices[-1]
                        + "'"
                    )
            else:
                self.help()

    def help(self, args: list = []):
        for cmd, info in self.cmds.items():
            self.console.print(f" [bold yellow]{cmd}[/]\t{info["help"]}")

    def quit(self, args: list):
        if self.loaded_module_driver:
            self.loaded_module_driver.stop()
        self.end_flag = True

    def load(self, args: list):
        if len(args) != 1:
            self.console.print("error: missing module name to load- canceled ")
            return
        if self.loaded_module_driver:
            self.loaded_module_driver.stop()
            self.found_modules = {}
        self.loaded_module_driver = self.module_handler.create_module(
            f"Module {args[0]}", args[0]
        )
        if self.loaded_module_driver:
            self.console.print(f"Module {args[0]} loaded")
        else:
            self.console.print(f"Error:  Failed to load Module {args[0]}")

    def scan(self, args: list):
        if not self.loaded_module_driver:
            self.console.print("No module loaded - Load a module first to scan")
            return
        self.found_modules = self.loaded_module_driver.scan()

    def flash(self, args: list):
        if len(args) != 1:
            self.console.print("error: missing module name to load- canceled ")
            return
        if not self.loaded_module_driver:
            self.console.print("No driver loaded - Load a module driver first to scan")
            return
        if not self.found_modules:
            self.console.print("No modules loaded - please check your setup and retry")
            return
        first_found_module = list(self.found_modules.values())[0]
        if not first_found_module.hardware_ok():
            self.console.print(
                "No valid Module hardware found - please check your setup and retry"
            )
            return
        self.console.print("Try to flash ")
        self.loaded_module_driver.flash(
            first_found_module, args[0], self.flash_progress_indicator
        )

    def erase(self, args: list):
        if not self.loaded_module_driver:
            self.console.print("No driver loaded - Load a module driver first to scan")
            return
        if not self.found_modules:
            self.console.print("No modules loaded - please check your setup and retry")
            return
        first_found_module = list(self.found_modules.values())[0]
        if not first_found_module.hardware_ok():
            self.console.print(
                "No valid Module hardware found - please check your setup and retry"
            )
            return
        self.console.print("Try to erase ")
        self.loaded_module_driver.erase(first_found_module)

    def parametrize(self, args: list):
        if len(args) != 2:
            self.console.print("error: wrong number of arguments ")
            return
        if not self.loaded_module_driver:
            self.console.print("No driver loaded - Load a module driver first for")
            return
        if not self.found_modules:
            self.console.print("No modules loaded - please check your setup and retry")
            return
        first_found_module = list(self.found_modules.values())[0]
        if not first_found_module.hardware_ok():
            self.console.print(
                "No valid Module hardware found - please check your setup and retry"
            )
            return
        self.console.print("Try to load parameter file")
        try:
            node_id = int(args[1], base=16)
        except:
            print(f"Error: node id {args[1]} is not a valid hex value")
            return
        try:
            with open(args[0], encoding="utf8") as fin:
                parameter_json = json.load(fin)
        except:
            print(
                f"Error: parameter file {args[0]} is not readable or does not contain valid json"
            )
            return
        self.loaded_module_driver.protocol_init(node_id)
        self.loaded_module_driver.write_parameters(parameter_json)

    def flash_progress_indicator(self, percentage):
        print(f"Flash progress {percentage}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--module", help="module folder to test", required=True)

    args = parser.parse_args()

    DirectoryMapper(
        os.path.abspath(os.path.dirname(__file__)),
        {
            "backup": "volumes/backup",
            "runtime": "volumes/runtime",
            "tmpfs": "volumes/tmpfs",
        },
    )

    cli = CLI(args.module)
