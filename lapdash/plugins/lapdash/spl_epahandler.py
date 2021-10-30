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
from base64 import b64encode
import argparse
import time
import copy
from io import StringIO
import threading
import uuid
from pprint import pprint

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
		self.modref = modref

		# do the plugin specific initialisation first

		self.lock = threading.Lock()

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

		if queue_event.type == defaults.MSG_SOCKET_CARDMENU_DELETE_REQUEST:
				if queue_event.user in []:
					pass
				self.movielist_storage.write(
					'movielist', self.movielist)

				movie_info_list = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_MOVIE_ID, queue_event.data['uri']))
				self.modref.message_handler.queue_event(queue_event.user, defaults.PLAYER_PLAY_REQUEST, {
					'user': queue_event.user,
				})

		with self.lock:
			self.create_new_movie_list_item()
		self.modref.message_handler.queue_event(queue_event.user, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_HOME_MOVIE_INFO_LIST, 'config': self.prepare_movie_list(queue_event.user)})
		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		# print("ui handler query handler", queue_event.type,  queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_VALID_MOVIE_RECORDS:
			return self.query_valid_movie_records(queue_event.params['source'])
		return[]

	def _run(self):
		''' starts the server
		'''
		while self.runFlag:
			act_secs = int(time.time())
			# time until the next full minute
			remaining_secs = act_secs % 60
			if remaining_secs:
				time.sleep(remaining_secs)
			with self.lock:
				self.request_stream_playlist()
				self.timer_record_request()

	def _stop(self):
		self.runFlag = False

	# ------ plugin specific routines

