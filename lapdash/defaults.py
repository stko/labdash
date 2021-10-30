#!/usr/bin/env python
# -*- coding: utf-8 -*-

CONFIG_FILE = 'config/config.json'
USER_DATA_FILE = 'config/users.json'
WEB_ROOT_DIR = '../web/'

# all the different message types
MSG_SOCKET_CONNECT = 'wsconnect'
MSG_SOCKET_CLOSE = 'wsclose'
MSG_SOCKET_CARDMENU_DELETE_REQUEST = 'cardmenu_delete_request'
MSG_SOCKET_EDIT_PLAY_REQUEST = 'edit_play_request'
MSG_SOCKET_EDIT_PLAY_ADD_REQUEST = 'edit_play_add_request'
MSG_SOCKET_EDIT_RECORD_ADD_REQUEST = 'edit_record_add_request'
MSG_SOCKET_MSG = 'wsmsg'
MSG_SOCKET_HOME_MOVIE_INFO_LIST = 'home_movie_info_list'
MSG_SOCKET_HOME_MOVIE_INFO_UPDATE = 'home_movie_info_update'
MSG_SOCKET_HOME_PLAY_REQUEST = 'home_play_request'
MSG_SOCKET_HOME_RECORD_REQUEST = 'home_record_request'
MSG_SOCKET_PLAYER_TIME = 'player_time'
MSG_SOCKET_PLAYER_KEY = 'player_key'
MSG_SOCKET_PLAYER_VOLUME = 'player_volume'
MSG_SOCKET_PLAYER_POSITION = 'player_position'
MSG_SOCKET_PLAYER_STOP_AND_RECORD = 'player_stop_and_record'
MSG_SOCKET_SELECT_PLAYER_DEVICE = 'select_player_device'
MSG_SOCKET_PLAYER_MOVIE_INFO = 'player_movie_info'
MSG_SOCKET_APP_USER_MESSAGE = 'app_user_message'

MSG_SOCKET_QUERY_FEASIBLE_DEVICES_ANSWER = 'player_device_info'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_SOURCES = 'edit_query_available_sources'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_SOURCES_ANSWER = 'edit_query_available_sources_answer'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_PROVIDERS = 'edit_query_available_providers'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_PROVIDERS_ANSWER = 'edit_query_available_providers_answer'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_CATEGORIES = 'edit_query_available_categories'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_CATEGORIES_ANSWER = 'edit_query_available_categories_answer'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_MOVIES = 'edit_query_available_movies'
MSG_SOCKET_EDIT_QUERY_AVAILABLE_MOVIES_ANSWER = 'edit_query_available_movies_answer'

# all the different query types
QUERY_FEASIBLE_DEVICES = 'feasibledevices'
QUERY_AVAILABLE_SOURCES = 'availablesources'
QUERY_AVAILABLE_PROVIDERS = 'availableproviders'
QUERY_AVAILABLE_CATEGORIES = 'availablecategories'
QUERY_AVAILABLE_MOVIES = 'availablemovies'
QUERY_MOVIE_ID = 'movieid'
QUERY_VALID_MOVIE_RECORDS = 'queryvalidmovierecords'

# player messages
PLAYER_PLAY_REQUEST = 'playerplayrequest'
PLAYER_PLAY_REQUEST_WITHOUT_DEVICE = 'playerplayrequestwithoutdevice'
PLAYER_SAVE_STATE_REQUEST = 'playersavestaterequest'

# device messages
DEVICE_PLAY_REQUEST = 'deviceplayrequest'
DEVICE_PLAY_PAUSE = 'deviceplaypause'
DEVICE_PLAY_RESUME = 'deviceplayresume'
DEVICE_PLAY_STOP = 'deviceplaystop'
DEVICE_PLAY_SETPOS = 'deviceplaysetpos'
DEVICE_PLAY_SETVOLUME = 'deviceplaysetvolume'
DEVICE_PLAY_STATUS = 'deviceplaystatus'

# stream messages
STREAM_REQUEST_PLAY_LIST = 'streamrequestplaylist'
STREAM_ANSWER_PLAY_LIST = 'streamanswerplaylist'

# limits the number of search results when do a query
MAX_QUERY_SIZE = 40

# movie types
MOVIE_TYPE_STREAM='stream'
MOVIE_TYPE_RECORD='record'
MOVIE_TYPE_TIMER='timer'
MOVIE_TYPE_TEMPLATE='template'
MOVIE_TYPE_RECORD_TEMPLATE='recordtemplate'

#Timer messages
TIMER_RECORD_REQUEST='timerrecordrequest'
TIMER_RECORD_RESULT='timerrecordresult'


# States of a record request
class Record_States:
	WAIT_FOR_RECORDING = 0
	ACTUAL_RECORDING = 1
	RECORDING_FINISHED = 2
	RECORDING_FAILED = 3  # something went wrong, no result

# Player states
PLAYER_STATE_EMPTY = 0 # actual no stream loaded
PLAYER_STATE_PLAY = 1 # actual playing stream
PLAYER_STATE_PAUSE = 2 # stream loaded, but on pause
