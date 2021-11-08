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
		self.instance=None
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
		print("epahandler event handler", queue_event.type, queue_event.user)

		if queue_event.type == defaults.EPA_LOADDIR:
				self.load_epa_dir(queue_event.data['actual_settings'])
				return None # event handled, no further processing
		if queue_event.type == defaults.EPA_LOAD_EPA:
				file_id=queue_event.data
				if file_id in self.epas:
					self.load_epa(self.epas[file_id])
				return None # event handled, no further processing
		if queue_event.type == defaults.MSG_SOCKET_BROWSER and self.instance:
				# let the ldmclass handle the event
				return self.instance.event_listener(queue_event)
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

	def load_epa_dir(self, actual_settings):
		self.epas = {}
		self.actual_settings=actual_settings.copy()
		self.themes_directory_path=os.path.join(self.actual_settings['www_root_dir'],'theme')
		regex = re.compile(r'^.+.epd$')
		try:
			list_subfolders_with_paths = [
				file_info for file_info in os.scandir(self.actual_settings['epa_root_dir']) if file_info.is_dir() and regex.match(file_info.name) ]
			self.theme_names = [
				file_info.name for file_info in os.scandir(self.themes_directory_path) if file_info.is_dir() ]
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
			
			self.modref.message_handler.queue_event(
				None, defaults.EPA_DIRECTORY, self.epas.copy()
			)

			self.construct_catalog()

		except Exception as e:
			print("Can't load plugin "+str(e))
			traceback.print_exc(file=sys.stdout)


	def load_epa(self, epa_info):
		''' inits the plugin
		'''
		try:
			module_spec = importlib.util.spec_from_file_location(epa_info['script'], epa_info['full_path_name'])
			my_module = importlib.util.module_from_spec(module_spec)
			# end a previous instance, if there is one
			if self.instance:
				self.instance.stop()
				self.instance = None
			module_spec.loader.exec_module(my_module)
			self.instance = my_module.LDM(self.modref.message_handler)
			self.epas[epa_info['file_id']]['instance'] =self.instance # ? I don't know for that might be used later, but I just keep it in :-)
			self.instance.run()
		except Exception as e:
			print("Can't load plugin "+str(e))
			traceback.print_exc(file=sys.stdout)

	def construct_catalog(self):
		'''
		creates the xml struct about the available content, which is tranfered to the Browser if the Browser goes on / and
		which then creates the catalog of available scripts
		'''

		# https://stackoverflow.com/a/61254611

		from lxml import etree as ET

		# Note the use of nsmap. The syntax used in the question is not accepted by lxml
		root_element = ET.Element("catalog")

		# Create PI and and insert it before the root element
		pi = ET.ProcessingInstruction("xml-stylesheet", text='type="text/xsl" href="/theme/default/xslt/start.xsl"')
		root_element.addprevious(pi)

		## here we had a list of different types connections in OOBD  - not needed anymore?

		element_node = ET.SubElement(root_element ,"connection")
		element_node.attrib['selected']='yes'
		element_node.text = "Default connection"
		
		# prepare a list of available themes
		for theme in self.theme_names:
			element_node = ET.SubElement(root_element ,"theme")
			if theme.lower() == self.actual_settings['theme'].lower():
				element_node.attrib['selected']='yes'
			element_node.text = theme

		# now we add the epa dirs
		for epa_info in self.epas.values():
			element_node = ET.SubElement(root_element ,"script")
			sub_element =ET.SubElement(element_node ,"fileid")
			sub_element.text = '/ld/'+epa_info['file_id']

			sub_element =ET.SubElement(element_node ,"filename")
			sub_element.text = epa_info['path']
			if epa_info['manifest']: # more data available

				# this is the list of optinonal values, which we copy, in case they are there
				optional_values={
					'title' : 'title',
					'name' : 'name',
					'shortname' : 'shortname',
					'description' : 'description',
					'version' : 'version',
					'copyright' : 'copyright',
					'author' : 'author',
					'security' : 'security',
					'date' : 'date',
					'icon' : 'icon',
					'screenshot' : 'screenshot',
					'url' : 'url',
					'email' : 'email',
					'phone' : 'phone',
					'html' : 'html',
				}

				for key, tag_name in optional_values.items():
					if key in epa_info['manifest']:
						value=epa_info['manifest'][key]
						sub_element =ET.SubElement(element_node ,tag_name)
						sub_element.text = value

		catalog_xml_string=ET.tostring(ET.ElementTree(root_element),encoding="utf-8",
										xml_declaration=True, pretty_print=True)
		self.modref.message_handler.queue_event(
			None, defaults.EPA_CATALOG, catalog_xml_string
		)

