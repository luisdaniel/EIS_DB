#coding: utf8 
from mongoengine import *
import models
from datetime import datetime
import logging
import os.path
import json
import csv
from collections import Counter
import numpy as np
import re
import bson
from elasticsearch import Elasticsearch as ES, RequestsHttpConnection as RC 
#from pyes import *

ES_USER=os.environ.get('ES_USER')
ES_PASS=os.environ.get('ES_PASS')
ES_HOST=os.environ.get('ES_HOST')
host_params = {'host':os.environ.get('ES_HOST'), 'port':80, 'use_ssl':False}
es = ES([host_params], connection_class=RC, http_auth=(ES_USER, ES_PASS),  use_ssl=False)

states ={"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", 
	"DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KA": "Kansas", 
	"KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", 
	"MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", 
	"NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", 
	"SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", 
	"WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico"}



class Search(object):
	def search(self, query, from_, size):
		res = es.search(index="eis", body={
			"query": {
				"query_string":{
					"fields":['title', 'state', 'agency'],
					"query":query
				}
			}
		}, ignore=[400, 404], from_=from_, size=size)
		return {"results":res['hits']['hits'], "size":res['hits']['total']}
