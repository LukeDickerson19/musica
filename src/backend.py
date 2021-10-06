
# front end libraries
from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia
import pyqtgraph as pg

# backend libraries
import os
import sys
import json
import time
import random
import subprocess
import threading
import queue
import numpy as np
import scipy
import sounddevice as sd
import pathlib
import pandas as pd
import numpy as np

# local libraries and file paths
REPO_PATH		= str(pathlib.Path(__file__).resolve().parent.parent)
SRC_PATH		= os.path.join(REPO_PATH, 'src')
UTILS_PATH		= os.path.join(REPO_PATH, 'common_utils')
IMAGES_PATH		= os.path.join(REPO_PATH, 'images')
STYLESHEETS_PATH = os.path.join(SRC_PATH,  'stylesheets')
sys.path.append(SRC_PATH)
sys.path.append(UTILS_PATH)
PROPERTY_FILEPATH = os.path.join(SRC_PATH, 'config.properties')
import general_utils
import logging_utils



# global variables

A_MAJOR = {
	1 : [  5,   None,  6,  None,  7,    1,   None,  2,  None,  3,    4,   None,  5,   None,  6,  None,  7,    1,   None,  2,  None,  3,   4,   None,  5  ],
	2 : [  2,   None,  3,   4,   None,  5,   None,  6,  None,  7,    1,   None,  2,   None,  3,   4,   None,  5,   None,  6,  None,  7,   1,   None,  2  ],
	3 : [ None,  7,    1,  None,  2,   None,  3,    4,  None,  5,   None,  6,   None,  7,    1,  None,  2,   None,  3,    4,  None,  5,  None,  6,   None],
	4 : [  4,   None,  5,  None,  6,   None,  7,    1,  None,  2,   None,  3,    4,   None,  5,  None,  6,   None,  7,    1,  None,  2,  None,  3,    4  ],
	5 : [  1,   None,  2,  None,  3,    4,   None,  5,  None,  6,   None,  7,    1,   None,  2,  None,  3,    4,   None,  5,  None,  6,  None,  7,    1  ],
	6 : [  5,   None,  6,  None,  7,    1,   None,  2,  None,  3,    4,   None,  5,   None,  6,  None,  7,    1,   None,  2,  None,  3,   4,   None,  5  ]
}
SCALE_NAMES = [
	'A major',
	'G# major',
	'G major',
	'F# major',
	'F major',
	'E major',
	'D# major',
	'D major',
	'C# major',
	'C major',
	'B major',
	'A# major'
]
MODE_NAMES = [
	'Ionian',
	'Dorian',
	'Phrygian',
	'Lydian',
	'Mixolydian',
	'Aeolian',
	'Locrian'
]


log_filepath = os.path.join(SRC_PATH, 'log.txt')
log = logging_utils.Log(log_filepath) # init log as global var so it doesn't need to be passed to functions
properties = general_utils.Properties(PROPERTY_FILEPATH)

# enum of views
class view:
	SOUND_WAVE  = 1
	# PIANO_KEYS  = 2
	# SHEET_MUSIC = 3
	# GUITAR_TAB  = 4
	# FRET_BOARD  = 5



class AudioInput:

	def __init__(self, num_indents=0, new_line_start=False):
		log.print('initializing audio input ...', num_indents=num_indents, new_line_start=new_line_start)
		self.device_name = properties.get('audio', 'device_name')
		self.input_device_index = None
		self.input_device_info  = None
		self.connected = False
		for i, d in enumerate(sd.query_devices()):
			if d['name'].startswith(self.device_name):
				self.input_device_index = i
				self.input_device_info = d
				break
		if self.input_device_index == None:
			log.print('failed to find device: %s' % self.device_name, num_indents=num_indents)
			return
		self.downsample	= properties.get('audio', 'downsample'); log.print('downsample: %s' % self.downsample, num_indents=num_indents+1)
		self.channels	= properties.get('audio', 'channels')
		self.mapping	= [c - 1 for c in self.channels] # Channel numbers start with 1
		self.q			= queue.Queue()
		self.samplerate = self.input_device_info["default_samplerate"]; log.print('samplerate: %s' % self.samplerate, num_indents=num_indents+1)
		self.stream = sd.InputStream(
			device=self.input_device_index,
			channels=max(self.channels),
			samplerate=self.samplerate,
			callback=self.audio_callback)
		self.connected = True
		self.stream.start()
		log.print('audio input initialized', num_indents=num_indents)

	def audio_callback(self, indata, frames, time, status):
		if status:
			print(status, file=sys.stderr)
		# print(len(indata), time)
		self.q.put(indata[::self.downsample, self.mapping])


