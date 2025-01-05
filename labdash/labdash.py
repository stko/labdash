#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
from labdash.directorymapper import DirectoryMapper

# from webserver import Webserver

from labdash.messagehandler import MessageHandler
from labdash import proglogger
from labdash.pluginmanager import PluginManager


class ModRef:
    """helper class to store references to the global modules"""

    def __init__(self):
        self.server = None
        self.message_handler = None


def _(s):
    return s


if __name__ == "__main__":
    logger = proglogger.getLogger(__name__)

    DirectoryMapper(
        os.path.abspath(os.path.dirname(__file__)),
        {
            "backup": "volumes/backup",
            "runtime": "volumes/runtime",
            "tmpfs": "volumes/tmpfs",
            "videos": "volumes/videos",
        },
    )
    modref = ModRef()  # create object to store all module instances
    modref.message_handler = MessageHandler(modref)
    # modref.server = Webserver(modref)
    plugin_manager = PluginManager(modref, "plugins")

    # modref.server.run()

    while True:
        time.sleep(1)
