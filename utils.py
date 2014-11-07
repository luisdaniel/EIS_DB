#coding: utf8 
from mongoengine import *
import models
from datetime import datetime
import logging
import os
import json
import csv
from collections import Counter
import numpy as np
import re
import bson

class PDFProcesser(object):
	def extract_text(self, filename):
		#code for stuff
		logging.info("process text")
