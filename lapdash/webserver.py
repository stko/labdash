#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json
from base64 import b64encode
import argparse
import time

from jsonstorage import JsonStorage
from flask import Flask, render_template, send_from_directory
from flask_sockets import Sockets, Rule
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from pprint import pprint

from io import StringIO
from splthread import SplThread
import defaults


# Add the directory containing your module to the Python path (wants absolute paths)

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))

sys.path.append(os.path.abspath(ScriptPath))

# own local modules


class WebsocketUser:
	'''handles all user related data
	'''

	def __init__(self, name, ws):
		self.name = name
		self.ws = ws


class Webserver(SplThread):

	def __init__(self, modref):
		''' creates the HTTP and websocket server
		'''

		self.modref = modref

		super().__init__(modref.message_handler, self)
		# reads the config, if any
		self.config = JsonStorage('webserver', 'backup', "config.json",
			{
				'server_config': {
					"credentials": "",
					"host": "0.0.0.0",
					"port": 8000,
					"secure": False
				},
			})
		server_config = self.config.read("server_config", {})
		# set up the argument parser with values from the config
		parser = argparse.ArgumentParser()
		parser.add_argument("--host", default=server_config["host"],
							help="the IP interface to bound the server to")
		parser.add_argument("-p", "--port", default=server_config["port"],
							help="the server port")
		parser.add_argument("-s", "--secure", action="store_true", default=server_config["secure"],
							help="use secure https: and wss:")
		parser.add_argument("-c", "--credentials",  default=server_config["credentials"],
							help="user credentials")
		self.args = parser.parse_args()

		self.app = Flask(__name__)
		self.sockets = Sockets(self.app)
		self.ws_clients = []  # my actual browser connections

		self.modref.message_handler.add_event_handler(
			'webserver', 0, self.event_listener)
		if self.args.secure:
			print('initialized secure https server at port %d' %
				  (self.args.port))
		else:
			print('initialized http server at port %d' % (self.args.port))

		# https://githubmemory.com/repo/heroku-python/flask-sockets/activity
		self.sockets.url_map.add(
			Rule('/ws', endpoint=self.on_create_ws_socket, websocket=True))

		@self.app.route('/')
		def index():
			return 'moin'

		@self.app.route('/libs/<path:path>')
		def send_libs(path):
			return send_from_directory('/home/steffen/Desktop/workcopies/lapdash/web/libs', path)

		@self.app.route('/theme/default/<path:path>')
		def send_theme(path):
			return send_from_directory('/home/steffen/Desktop/workcopies/lapdash/web/theme/default', path)

	def on_create_ws_socket(self, ws):
		''' distributes incoming messages to the registered event handlers

		Args:
			message (:obj:`str`): json string, representing object with 'type' as identifier and 'config' containing the data
		'''
		user=self.find_user_by_ws(ws)
		if user:
			if user != ws:
				self.disconnect()
				user=self.connect(ws)
		else:
			user=self.connect(ws)
		while not ws.closed:
			message = ws.receive()
			if message:
				#self.log_message('websocket received "%s"', str(message))
				try:
					data = json.loads(message)
					self.modref.message_handler.queue_event(
						user.name, defaults.MSG_SOCKET_BROWSER, data)
				except:
					#self.log_message('%s', 'Invalid JSON')
					pass
				#self.log_message('json msg: %s', message)

	def connect(self, ws):
		''' thows a connect event about that new connection
		'''
		#self.log_message('%s', 'websocket connected')
		# this is just a leftover from a previous multi - ws project, but maybe we'll need it again?
		user = WebsocketUser(None, ws)
		self.ws_clients.append(user)
		self.modref.message_handler.queue_event(
			user.name, defaults.MSG_SOCKET_CONNECT, None)
		self.emit(defaults.MSG_SOCKET_WSCONNECT, {'script': 'Python_sim'})
		self.emit('WRITESTRING', {'data': 'bla'})
		self.modref.message_handler.queue_event(
			user.name, defaults.EPA_LOADDIR, {'epa_dir': None})
		return user

	def find_user_by_ws(self, ws):
		for user in self.ws_clients:
			if user.ws == ws:
				return user
		return None

	def find_user_by_user_name(self, user_name):
		for user in self.ws_clients:
			if user.name == user_name:
				return user
		return None

	def disconnect(self):
		''' thows a close event about the closed connection
		'''

		user = self.find_user_by_user_name(None)
		if user:
			user.ws.close()
			self.ws_clients.remove(user)
		self.ws = None
		#self.log_message('%s', 'websocket closed')
		self.modref.message_handler.queue_event(
			self.user, defaults.MSG_SOCKET_CLOSE, None)

	def emit(self, type, config):
		''' sends data object as JSON string to websocket client

		Args:
		type (:obj:`str`): string identifier of the contained data type
		config (:obj:`obj`): data object to be sent
		'''

		message = {'type': type, 'config': config}
		user = self.find_user_by_user_name(None)
		pprint(message)
		if user.ws:
			if not user.ws.closed:
				user.ws.send(json.dumps(message))
			else:
				self.ws_clients.remove(user)

	def event_listener(self, queue_event):
		''' checks all incoming queue_events if to be send to one or all users
		'''
		#print("webserver event handler",queue_event.type,queue_event.user)
		if queue_event.type == defaults.MSG_SOCKET_MSG:
			message = {'type': queue_event.data['type'], 'config': queue_event.data['config']}
			json_message=json.dumps(message)
			for user in self.ws_clients:
				if queue_event.user == None or queue_event.user == user.name:
					user.ws.send(json_message)
			return None  # no futher handling of this event
		# for further pocessing, do not forget to return the queue event
		return queue_event

	def _run(self):
		''' starts the server
		'''

		try:
			origin_dir = os.path.dirname(__file__)
			web_dir = os.path.join(os.path.dirname(
				__file__), defaults.WEB_ROOT_DIR)
			os.chdir(web_dir)

			self.server = pywsgi.WSGIServer(
				(self.args.host, self.args.port), self.app, handler_class=WebSocketHandler)
			self.server.serve_forever()
			os.chdir(origin_dir)
		except KeyboardInterrupt:
			print('^C received, shutting down server')
			self.server.stop()

	def _stop(self):
		self.server.stop()

	def query_handler(self, queue_event, max_result_count):
		''' handler for system queries
		'''
		pass


if __name__ == '__main__':
	class ModRef:
		store = None
		message_handler = None

	modref = ModRef()
	ws = Webserver(modref)
	ws.run()
	while True:
		time.sleep(1)
	ws.stop()
