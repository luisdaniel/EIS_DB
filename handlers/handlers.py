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
import timeit


# the main page
class MainHandler(tornado.web.RequestHandler):
    def get(self):
    	display_from = int(self.get_argument("view", 0))
        display_num = int(self.get_argument("display", 100))
        state = self.get_argument("state", "")
        agency = self.get_argument("agency", "")
        date_from = self.get_argument("date_from", "")
        date_to = self.get_argument("date_to", "")
        # final = self.get_argument("final_eis_only", "")
        if date_from:
            date_from_f = datetime.strptime(date_from, "%m/%d/%Y").strftime("%Y-%m-%d")
        else:
            date_from_f = "1900-01-01"
        if date_to:
            date_to_f = datetime.strptime(date_to, "%m/%d/%Y").strftime("%Y-%m-%d")
        else:
            date_to_f = "2030-01-01"
        # if final =='on':
        #     doc_type = "final"
        # else:
        #     doc_type = ""
        q = (Q(state__contains=state) & 
            Q(agency__contains=agency) & 
            Q(federal_register_date__gte=date_from_f) &
            Q(federal_register_date__lte=date_to_f))
    	reports = models.Report.objects(q).only(
            'title', 
            'eis_number',
            'federal_register_date').order_by(
            '-federal_register_date').skip(display_from).limit(display_num)
        total_hits = models.Report.objects(q).count()
        #reports = reports[display_from:display_from+display_num]
        total_reports = models.Report.objects().count()
        self.render(
            "index.html",
            page_title='Heroku Funtimes',
            page_heading='Hi!',
            reports = reports,
            states = states,
            state_abbrev_list=state_abbrev_list,
            agencies=agencies,
            agencies_abbrev_list=agencies_abbrev_list,
            display_from=display_from,
            display_num=display_num,
            total_hits=total_hits,
            total_reports=total_reports,
            q = {"s":state, "a":agency, "df":date_from, "dt":date_to}
        )

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        search_params = {
            "query": self.get_argument("query", None),
            "state": self.get_argument("state", None),
            "agency": self.get_argument("agency", None),
            "date_from": self.get_argument("date_from", None),
            "date_to": self.get_argument("date_to", None),
            "include_letters": self.get_argument("include_letters", None),
            "final_eis_only": self.get_argument("final_eis_only", None),
            "display_from": int(self.get_argument("view", 0)),
            "display_num": int(self.get_argument("display", 100))}
        if search_params['date_from']:
            search_params['date_from'] = datetime.strptime(
                search_params['date_from'], "%m/%d/%Y").strftime("%Y-%m-%d")
        if search_params['date_to']:
            search_params['date_to'] = datetime.strptime(
                search_params['date_to'], "%m/%d/%Y").strftime("%Y-%m-%d")
        if not search_params['query']:
            results = None
            total_hits = None
        else:
            results = self.application.search.search(search_params)
            total_hits = results['total_hits']
            results = results['hits']
        # for r in results:
        #     logging.info(r['fields']['title'])
        #     logging.info(r['fields']['date'])
        self.render(
            "search.html",
            page_title='Search EI Statements',
            results = results,
            states = states,
            state_abbrev_list=state_abbrev_list,
            agencies=agencies,
            agencies_abbrev_list=agencies_abbrev_list,
            total_hits = total_hits,
            display_from=search_params['display_from'],
            display_num=search_params['display_num'],
            query=search_params['query']
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

class AdvancedSearchHandler(tornado.web.RequestHandler):
    def get(self):
        query = self.get_argument("query", None)
        display_from = int(self.get_argument("view", 0))
        display_num = int(self.get_argument("display", 100))
        if not query:
            results = None
            total_hits = None
        else:
            results = self.application.search.advancedSearch(
                query, 
                display_from, 
                display_num)
            total_hits = results['total_hits']
            results = self.application.tools.pack_search_results(
                results['hits'])
        self.render(
            'search_files.html',
            page_title="Advanced Search",
            page_heading="Advanced Search",
            results = results,
            total_hits=total_hits,
            display_from=display_from,
            display_num=display_num,
            query=query
        )


class NotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "404.html",
            page_title='404 - Not Found',
            page_heading='Not Found',
        )