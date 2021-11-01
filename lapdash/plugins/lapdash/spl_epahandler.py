#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
from messagehandler import Query

import defaults
from splthread import SplThread
from jsonstorage import JsonStorage
import sys
import os
import ssl
import json
import importlib
import traceback
from base64 import b64encode
import base64
import time
import re
from io import StringIO
import threading
import uuid
from pprint import pprint
import proglogger

logger = proglogger.getLogger(__name__)
# Non standard modules (install with pip)

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules


class SplPlugin(SplThread):
	plugin_id = 'epahandler'
	plugin_names = ['EPA Handler']

	def __init__(self, modref):
		''' inits the plugin
		'''
		self.config = JsonStorage('EpaHandler', 'backup', "config.json", {
			}
		)
		self.modref = modref

		# do the plugin specific initialisation first

		self.lock = threading.Lock()

		self.epas = {}

		# at last announce the own plugin
		super().__init__(modref.message_handler, self)
		modref.message_handler.add_event_handler(
			self.plugin_id, 0, self.event_listener)
		modref.message_handler.add_query_handler(
			self.plugin_id, 0, self.query_handler)
		self.runFlag = True

	def event_listener(self, queue_event):
		''' 
		'''
		#print("epahandler event handler", queue_event.type, queue_event.user)

		if queue_event.type == defaults.EPA_LOADDIR:
				self.load_epa_dir(queue_event.data['epa_dir'])
				if self.epas:
					self.load_epa(list(self.epas.values())[0])
				return None # event handled, no further processing

		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		# print("ui handler query handler", queue_event.type,  queue_event.user, max_result_count)
		#if queue_event.type == defaults.QUERY_VALID_MOVIE_RECORDS:
		#	return self.query_valid_movie_records(queue_event.params['source'])
		return[]

	def _run(self):
		''' starts the server
		'''
		self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
		'type': defaults.MSG_SOCKET_WRITESTRING, 'config': {'data':'epa'}})


		while self.runFlag:
			act_secs = int(time.time())
			# time until the next full minute
			remaining_secs = act_secs % 60
			if remaining_secs:
				time.sleep(remaining_secs)
			with self.lock:
				pass

	def _stop(self):
		self.runFlag = False

	# ------ plugin specific routines

	def load_epa_dir(self, epa_root_dir=None):
		if not epa_root_dir:
			epa_root_dir=self.config.read('epa_root_dir')
		else:
			self.config.write('epa_root_dir',epa_root_dir)
		self.epas = {}
		regex = re.compile(r'^.+.epd$')
		try:
			list_subfolders_with_paths = [
				file_info for file_info in os.scandir(epa_root_dir) if file_info.is_dir() and regex.match(file_info.name) ]
			for file_info in list_subfolders_with_paths:
				script=None
				# does a manifest file exist?
				try: 
					manifest=json.load(open(os.path.join(file_info.path,'manifest')))
					if 'script' in manifest:
						potential_source=os.path.join(file_info.path,manifest['script'])
						if os.path.exists(potential_source):
							script=manifest['script']
					else:
						potential_source=os.path.join(file_info.path,'main.py')
						if os.path.exists(potential_source):
							script='main.py'
					if not script:
						logger.warning(f'no (default) script given in {file_info.path}')
						continue

				except: 
					logger.warning(f'no readable manifest in {file_info.path}')
					continue
				file_id = base64.b64encode(file_info.name.encode()).decode().replace('\n','')
				self.epas[file_id]={
					'file_id' : file_id,
					'manifest': manifest,
					'path' : file_info.path,
					'script': script,
					'full_path_name' : os.path.join(file_info.path,script)
					}

		except Exception as e:
			print("Can't load plugin "+str(e))
			traceback.print_exc(file=sys.stdout)


	def load_epa(self, epa_info):
		''' inits the plugin
		'''
		try:

			module_spec = importlib.util.spec_from_file_location(epa_info['script'], epa_info['full_path_name'])
			my_module = importlib.util.module_from_spec(module_spec)
			module_spec.loader.exec_module(my_module)
			instance = my_module.LDM(self.modref.message_handler)
			self.epas[epa_info['file_id']]['instance'] =instance
			instance.run()
		except Exception as e:
			print("Can't load plugin "+str(e))
			traceback.print_exc(file=sys.stdout)


