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
    	reports = models.Report.objects().only('title', 'eis_number', 'date_uploaded').order_by('-date_uploaded')[:100]
        self.render(
            "index.html",
            page_title='Heroku Funtimes',
            page_heading='Hi!',
            reports = reports
        )

class ReportHandler(tornado.web.RequestHandler):
	def get(self, eis):
		try:
			logging.info("getting: " + str(eis))
			report = models.Report.objects.get(eis_number=eis)
			self.render(
	            "report.html",
	            page_title='Heroku Funtimes',
	            page_heading='Hi!',
	            report = report
	        )
		except Exception, e:
			logging.info("Could not get report: " + str(e))
			self.redirect('/404/')

class NotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "404.html",
            page_title='404 - Not Found',
            page_heading='Not Found',
        )