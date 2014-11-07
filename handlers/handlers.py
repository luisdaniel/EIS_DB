#!/usr/bin/env python
import os.path
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


#Mongo
from mongoengine import *
import models
import bson
from bson import json_util
import csv
import json
import re
import bcrypt
from datetime import datetime
from utils import *

# the main page
class MainHandler(tornado.web.RequestHandler):
    def get(self, q):
    	#display first 100 reports
    	reports = models.Report.objects().only('title', 'eis_number', 'date_uploaded')
        self.render(
            "index.html",
            page_title='Heroku Funtimes',
            page_heading='Hi!',
            reports = reports
        )

class ReportHandler(tornado.web.RequestHandler):
	def get(self, eis):
		try:
			report = models.Report.objects.get(eis_number=eis)
			self.render(
	            "report.html",
	            page_title='Heroku Funtimes',
	            page_heading='Hi!',
	            report = report
	        )
		except Exception, e:
			logging.info("Could not get report: " + str(e))
			self.render(
	            "404.html",
	            page_title='Not Found',
	            page_heading='EIS Report not found'
	        )