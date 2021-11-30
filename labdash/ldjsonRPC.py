#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import traceback
import json
from urllib.parse import urlparse, urlunparse
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError


def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


def dprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


def ldjsonRPC(host_url, action, data_dict):
	'''
	sends a jsonRPC

	TODO actual just hand written simple code, would be good to replace it with a proper jsonRPC library some day...
	'''

	url_elements = urlparse(host_url, action, data_dict)
	auth=None
	if url_elements.username and url_elements.password:
		auth=HTTPBasicAuth( url_elements.username, url_elements.password)
	try:
		resp = requests.post(host_url, auth=auth,
			json={
				"action": action,
				action: data_dict
			},
				verify=False
				)
		resp.raise_for_status()
		# access JSOn content
		jsonResponse = resp.json()
		print("Entire JSON response for report")
		print(jsonResponse)
		if jsonResponse['errorcode']:
			return True # something went wrong, so better no download
		result= jsonResponse['data']
		return result

	except HTTPError as http_err:
		print(f'HTTP error occurred: {http_err}')
	except Exception as err:
		print(f'Other error occurred: {err}')
	return True # something went wrong, so better no download



if __name__ == '__main__':
	ldjsonRPC(sys.argv[1],'log_entry',{'mgs':'Jason was here'})

