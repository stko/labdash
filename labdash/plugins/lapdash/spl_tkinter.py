#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

import time

from jsonstorage import JsonStorage
from lxml import objectify

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from pprint import pprint

from splthread import SplThread
import defaults


# Add the directory containing your module to the Python path (wants absolute paths)

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))

sys.path.append(os.path.abspath(ScriptPath))



class SplPlugin(SplThread):
	plugin_id = 'tkinter'
	plugin_names = ['TKinter UI']

	def __init__(self, modref):
		''' creates the HTTP and websocket server
		'''

		self.modref = modref

		super().__init__(modref.message_handler, self)
		# reads the config, if any
		self.config = JsonStorage('tkinter', 'backup', "config.json",
			{
				"actual_settings": {
					"theme": "default",
					"www_root_dir": "C:\\Users\\koehler\\Desktop\\Workcopies\\labdash\\web",
					"epa_root_dir": "C:\\Users\\koehler\\Desktop\\Workcopies\\labdash_internals"
    			}
			})
		self.setting=self.config.read('actual_settings')

		self.actual_file_id=None
		self.awaiting_initial_content_list=True
		self.modref.message_handler.add_event_handler(
			'tkinter', 0, self.event_listener)

	def handle_epa(self,path):
		'''
		path: relative (url) path of the EPA directory to run
		'''
		elements=path.split('/') # first we split the path into pieces
		if not elements: # empty path
			print("Error: No EPA Dir given")
			return
		if len(elements)==1: # this is a request to load a new EPA
			if not elements[0] in self.epa_directoy:
				print("Error:Unknown EPA reference in URL")
				return
			self.actual_file_id=elements[0]
			epa_info=self.epa_directoy[elements[0]]
			if 'html' in epa_info: # does this package has its own main html page?
				print("Error: Tinter interface can not halnde custom html sheets")
				return
			else:
				print('ready to start the tinker screen')
				return
				#return send_from_directory(os.path.join(self.config.read('actual_settings')['www_root_dir'],'theme',self.theme), 'startpage.html')


		# we serve the file from within an epa directory
		return 

	def event_listener(self, queue_event):
		''' checks all incoming queue_events if to be send to one or all users
		'''
		print("tkinter event handler",queue_event.type,queue_event.user)
		if queue_event.type == defaults.MSG_SOCKET_MSG:
			# und hier muß jetzt der Tinter - Bildschirm gebaut werden
			print(queue_event.data)
			return None  # no futher handling of this event
		if queue_event.type == defaults.EPA_CATALOG:
			self.epa_catalog = objectify.fromstring(queue_event.data)
			# we need to start the server, if the initial catalog is available
			if self.awaiting_initial_content_list:
				self.awaiting_initial_content_list=False
			return None  # no futher handling of this event
		if queue_event.type == defaults.EPA_DIRECTORY:
			self.epa_directoy=queue_event.data
			return None  # no futher handling of this event
		# for further pocessing, do not forget to return the queue event
		return queue_event

	def _run(self):
		''' starts the server
		'''
		try:
			## read the epa dir with the actual settings
			self.modref.message_handler.queue_event(
				None, defaults.EPA_LOADDIR, {
					'actual_settings': self.config.read('actual_settings')
				}
			)
			while self.awaiting_initial_content_list:
				time.sleep(0.3)

			#os.chdir(origin_dir)
		except KeyboardInterrupt:
			print('^C received, shutting down server')

	def _stop(self):
		pass

	def query_handler(self, queue_event, max_result_count):
		''' handler for system queries
		'''
		pass




if __name__ == '__main__':
	class ModRef:
		store = None
		message_handler = None

	modref = ModRef()
	ws = SplPlugin(modref)
	ws.run()
	while True:
		time.sleep(1)
	ws.stop()
