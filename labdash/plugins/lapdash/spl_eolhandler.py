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
	plugin_id = 'eolhandler'
	plugin_names = ['EOL Handler']

	def __init__(self, modref):
		''' inits the plugin
		'''

		self.config = JsonStorage('eolhandler', 'backup', "config.json",
			{
				'modules_dir': [os.path.realpath(os.path.join(self.program_dir,'../../../modules/'))]
			})

		self.modref = modref

		# do the plugin specific initialisation first

		self.lock = threading.Lock()
		self.main_script_directory=os.path.abspath( os.path.dirname(sys.argv[0]))
		self.eols = {}
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
		#print("eolhandler event handler", queue_event.type, queue_event.user)

		if queue_event.type == defaults.EOL_LOADDIR:
				self.load_eol_dir(queue_event.data['actual_settings'])
				return None # event handled, no further processing
		if queue_event.type == defaults.EOL_LOAD_EOL:
				file_id=queue_event.data
				if file_id in self.eols:
					self.load_eol(self.eols[file_id])
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
		'type': defaults.MSG_SOCKET_WRITESTRING, 'config': {'data':'eol'}})

		self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
		'type': defaults.CM_EOL_EOLLIST, 'config': {
			'title': "EOL from Server",
			"items":[
				{
					"id":"4711",
					"parent":None,
					"text":"master"
				},
				{
					"id":"4712",
					"parent":"4711",
					"text":"bla"
				}
			]
		}})


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

	def load_eol_dir(self, actual_settings):
		self.eols = {}
		self.actual_settings=actual_settings.copy()
		self.themes_directory_path=os.path.join(self.actual_settings['www_root_dir'],'theme')
		regex = re.compile(r'^.+.eol$')
		try:
			list_subfolders_with_paths=[]
			for eol_root_dir in self.actual_settings['eol_root_dir']:
				list_subfolders_with_paths.extend( [
					file_info for file_info in os.scandir(os.path.join(self.main_script_directory,eol_root_dir)) if file_info.is_dir() and regex.match(file_info.name) ])
			self.theme_names = [
				file_info.name for file_info in os.scandir(os.path.join(self.main_script_directory,self.themes_directory_path)) if file_info.is_dir() ]
			for file_info in list_subfolders_with_paths:
				script=None
				procedures=None
				# does a manifest file exist?
				try: 
					manifest=json.load(open(os.path.join(file_info.path,'manifest'),encoding='UTF-8'))
					if 'script' in manifest:
						script_path=os.path.join(file_info.path,manifest['script'])
						if os.path.exists(script_path):
							script=manifest['script']
					else:
						script_path=os.path.join(file_info.path,'eolprocessor.py')
						if os.path.exists(script_path):
							script='eolprocessor.py'
					if not script:
						logger.warning(f'no (default) script given in {file_info.path}')
						continue
					'''
					 Design question: do we need the procedures coming from the manifest?

					 Actual they are searched in eolclass.load_procedures

					if 'procedures' in manifest:
						potential_source=os.path.join(file_info.path,manifest['procedures'])
						if os.path.exists(potential_source):
							procedures=manifest['procedures']
					else:
						potential_source=os.path.join(file_info.path,'procedures.yaml')
						if os.path.exists(potential_source):
							procedures='procedures.yaml'
					if not procedures:
						logger.warning(f'no (default) procedures given in {file_info.path}')
						continue
					'''
				except: 
					logger.warning(f'no readable manifest in {file_info.path}')
					continue
				file_id = base64.b64encode(file_info.name.encode()).decode().replace('\n','')
				self.eols[file_id]={
					'file_id' : file_id,
					'manifest': manifest,
					'path' : file_info.path,
					'script': script,
					# 'procedures': procedures,
					'full_path_name' : os.path.join(file_info.path,script)
					}
			
			self.modref.message_handler.queue_event(
				None, defaults.EOL_DIRECTORY, self.eols.copy()
			)

			self.construct_catalog()

		except Exception as e:
			print("Can't load plugin "+str(e))
			traceback.print_exc(file=sys.stdout)


	def load_eol(self, eol_info):
		''' inits the plugin
		'''
		try:
			module_spec = importlib.util.spec_from_file_location(eol_info['script'], eol_info['full_path_name'])
			my_module = importlib.util.module_from_spec(module_spec)
			# end a previous instance, if there is one
			if self.instance:
				self.instance.stop()
				self.instance = None
			module_spec.loader.exec_module(my_module)
			self.instance = my_module.EOL(self.modref.message_handler,eol_info['path'],self.config['modules_dir'])
			self.eols[eol_info['file_id']]['instance'] =self.instance # ? I don't know for that might be used later, but I just keep it in :-)
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
		pi = ET.ProcessingInstruction("xml-stylesheet", text='type="text/xsl" href="/theme/default/xslt/starteol.xsl"')
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

		# now we add the eol dirs
		for eol_info in self.eols.values():
			element_node = ET.SubElement(root_element ,"script")
			sub_element =ET.SubElement(element_node ,"fileid")
			sub_element.text = '/eol/'+eol_info['file_id']

			sub_element =ET.SubElement(element_node ,"filename")
			sub_element.text = eol_info['path']
			if eol_info['manifest']: # more data available

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
					if key in eol_info['manifest']:
						value=eol_info['manifest'][key]
						sub_element =ET.SubElement(element_node ,tag_name)
						sub_element.text = value

		catalog_xml_string=ET.tostring(ET.ElementTree(root_element),encoding="utf-8",
										xml_declaration=True, pretty_print=True).decode()
		self.modref.message_handler.queue_event(
			None, defaults.EOL_CATALOG, catalog_xml_string
		)

