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
    def get(self):
    	#display first 100 reports
        logging.info(ES_HOST)
    	display_from = int(self.get_argument("view", 0))
        display_num = int(self.get_argument("display", 100))
    	reports = models.Report.objects().only('title', 
            'eis_number', 'date_uploaded').order_by('-date_uploaded')[display_from:display_from+display_num]
        self.render(
            "index.html",
            page_title='Heroku Funtimes',
            page_heading='Hi!',
            reports = reports,
            display_from=display_from,
            display_num=display_num
        )

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        query = self.get_argument("query", None)
        display_from = int(self.get_argument("view", 0))
        display_num = int(self.get_argument("display", 100))
        if not query:
            results = None
        else:
            results = self.application.search.search(query, display_from, display_num)
        self.render(
            "search.html",
            page_title='Search EI Statements',
            results = results,
            display_from=display_from,
            display_num=display_num,
            query=query
        )

class ReportHandler(tornado.web.RequestHandler):
	def get(self, eis):
		try:
			logging.info("getting: " + str(eis))
			report = models.Report.objects.get(eis_number=eis)
		except Exception, e:
			logging.info("Could not get report: " + str(e))
			self.redirect('/404/')
		if report:
			self.render(
	            "report.html",
	            page_title='Heroku Funtimes',
	            page_heading='Hi!',
	            report = report
	        )

class NotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "404.html",
            page_title='404 - Not Found',
            page_heading='Not Found',
        )