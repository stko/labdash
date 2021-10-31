#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import threading
import time
from abc import ABCMeta, abstractmethod
import defaults
import traceback

class LDMClass(metaclass=ABCMeta):
	'''Partly abstract class as base class for LabDash modules
	'''

	def __init__(self, msg_handler):
		self.msg_handler = msg_handler

	def  event_listener(self, queue_event):
		''' handler for system events
		'''
		pass

	def query_handler(self, queue_event, max_result_count):
		''' handler for system queries
		'''
		pass


	def run(self):
		''' starts the child thread
		'''
		'''  #### first we try without being a thread
		# Create a Thread with a function without any arguments
		#th = threading.Thread(target=_ws_main, args=(server,))
		self.th = threading.Thread(target=self.child._run)
		# Start the thread
		self.th.setDaemon(True)
		self.th.start()
		'''
		self.execute_method_by_name('main', None,None)

	def stop(self, timeout=0):
		''' stops the child thread. If timeout > 0, it will wait timeout secs for the thread to finish
		'''
		'''  #### first we try without being a thread
		self.child._stop()
		if timeout > 0:
			self.th.join(timeout)
		return self.th.isAlive()
		'''
		
	def execute_method_by_name(self, name, oldvalue,id):
		try:
			return getattr(self, name)(oldvalue,id)
		except Exception as e:
			print(f"Can't execute method {name} "+str(e))
			traceback.print_exc(file=sys.stdout)


	# implementation of the old OOBD lua interface commands

	def openPage(self,name):
		self.msg_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type':defaults.CM_PAGE,
			'config': {
				'data':name
			}
		})

	def addElement(self, tooltip, name,value, oobdElementFlags=None, optid=None, optTable=None ):
		msg={
			'tooltip' : tooltip,
			'name' : name,
			'value' : value,
			
			}
		if oobdElementFlags:
			msg['FN_UPDATEOPS'] = oobdElementFlags
		if optid:
			msg['optid'] = optid
		if optTable:
			msg['opts'] = optTable
		self.msg_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': defaults.CM_VISUALIZE,
			'config': msg
		})

	def pageDone(self):
		self.msg_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': defaults.CM_PAGEDONE,
			'config': {}
		})
		

	def openXCVehicleData(*args, **kwargs):
		print('Warning: Call of non implemented legacy function xx()')

	def serReadLn(*args, **kwargs):
		print('Warning: Call of non implemented legacy function xx()')

	def serWait(*args, **kwargs):
		print('Warning: Call of non implemented legacy function xx()')

	def serSleep(delay):
		time.sleep(delay)

	def serWrite(*args, **kwargs):
		print('Warning: Call of non implemented legacy function xx()')

	def serFlush(*args, **kwargs):
		print('Warning: Call of non implemented legacy function xx()')

	def serDisplayWriteCall(self, text,cmd=None):
		msg={
			'command' : 'serDisplayWrite',
			'data' : text,
			}
		if cmd:
			msg['modifier'] = cmd
		self.msg_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_WRITESTRING,
			'config': msg
		})

	def msgBox(self, typeOfBox,title,text,default):
		typeOfBox=typeOfBox.lower()
		if typeOfBox=='alert':
			print('Warning: Call of non implemented legacy function msgBox() with internal alert')
			return
		msg={
			defaults.CM_PARAM : {
			'type' : 'String',
			'title' : title,
			'text' : text,
			'default' : default,
			}
			}
		if typeOfBox=='confirm':
			msg['confirm'] = 'yes'

		self.msg_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': defaults.CM_PARAM,
			'config': msg
		})
		print('Warning: Waiting for answer in msgBox() not correctly implemented yet')

	def onionMsg(*args, **kwargs):
		print('Warning: Call of non implemented legacy function onionMsg()')

	def dbLookup(*args, **kwargs):
		print('Warning: Call of non implemented legacy function dbLookup()')

	def ioInput(*args, **kwargs):
		print('Warning: Call of non implemented legacy function ioInput()')

	def ioRead(*args, **kwargs):
		print('Warning: Call of non implemented legacy function ioRead()')

