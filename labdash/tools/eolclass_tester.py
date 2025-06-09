#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

from rich.prompt import Confirm
from rich.console import Console
from labdash import eolclass


class CLI:
    """
    handle the user inputs
    """

    def __init__(self,module_dir:str):
        self.module_handler = eolclass.EOLClass(
            None,
            module_dir,
            [module_dir],
        )
        self.actual_module=None
        self.console = Console()
        self.end_flag = False
        self.cmds = {
            "quit": {"help": "Quits the program", "f": self.quit},
            "help": {"help": "print this help", "f": self.help},
            "load": {"load": "load the given module by its name as current module", "f": self.load},
        }
        while not self.end_flag:
            input = self.console.input("Your command (enter for help): ")
            if input:
                elements = input.split()
                choices = []
                for cmd, info in self.cmds.items():
                    if cmd.startswith(elements[0].lower()):
                        choices.append(cmd)
                if len(choices) == 1:
                    info = self.cmds[choices[0]]
                    if info["f"] != None:
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
        self.end_flag = True
    
    def load(self, args: list):
        if len(args)!= 1:
            self.console.print("error: missing module name to load- canceled ")
        self.console.print(f"try to load{args[0]}")
        self.actual_module=self.module_handler.create_module(f"Module {args[0]}", args[0])
        

    def get_args_int(self, args: list) -> list:
        numeric_args = []
        for arg in args:
            try:
                index = int(arg) - 1
                if index > -1 and index < len(self.dir_content.ignores):
                    numeric_args.append(int(arg) - 1)
            except:
                self.console.print(f"Error: '{arg}' is no numeric value!")
                return []
        return numeric_args



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--module",
        help="module folder to test",
        required=True
    )


    args = parser.parse_args()


    cli = CLI(args.module)
