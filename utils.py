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
import timeit
#from pyes import *

ES_USER=os.environ.get('ES_USER')
ES_PASS=os.environ.get('ES_PASS')
ES_HOST=os.environ.get('ES_HOST')
host_params = {'host':os.environ.get('ES_HOST'), 'port':80, 'use_ssl':False}
es = ES(
	[host_params], 
	connection_class=RC, 
	http_auth=(ES_USER, ES_PASS),  
	use_ssl=False)

states = {
		"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", 
		"CA": "California", "CO": "Colorado", "CT": "Connecticut", 
		"DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", 
		"GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", 
		"IN": "Indiana", "IA": "Iowa", "KA": "Kansas", "KY": "Kentucky", 
		"LA": "Louisiana", "ME": "Maine", "MD": "Maryland", 
		"MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", 
		"MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", 
		"NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", 
		"NM": "New Mexico", "NY": "New York", "NC": "North Carolina", 
		"ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", 
		"PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", 
		"SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", 
		"VT": "Vermont", "VA": "Virginia", "WA": "Washington", 
		"WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", 
		"PR": "Puerto Rico"
	}

state_abbrev_list = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", 
                "GA", "HI", "ID", "IL", "IN", "IA", "KA", "KY", "LA", "ME", "MD", 
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", 
                "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", 
                "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

agencies = {
		'BPA':'Bonneville Power Administration',
		'FSA':'',
		'FERC':'Federal Energy Regulatory Commission',
		'DOI':'Department of the Interior',
		'BR':'',
		'USA':'',
		'USN':'',
		'USAF':'US Air Force',
		'DOE':'Department of Energy',
		'GSA':'General Services Administration',
		'BOEM':'Bureau of Ocean Energy Management',
		'USCG':'US Coast Guard',
		'NPS':'National Park Service',
		'EPA':'Environmental Protection Agency',
		'DOS':'Department of State',
		'USMC':'US Marine Corps',
		'DOT':'Department of Transportation',
		'HUD':'',
		'NSF':'National Science Foundation',
		'BIA':'Bureau of lndian Affairs',
		'OSM':'Office of Surface Mining Reclamation and Enforcement',
		'DOC':'Department of Commerce',
		'NNSA':'National Nuclear Security Administration',
		'FAA':'Federal Aviation Administration',
		'AFS':'',
		'VA':'Veterans Affairs',
		'FRA':'Federal Railroad Administration',
		'USDA':'US Department of Agriculture',
		'STB':'Surface Transportation Board',
		'NHTSA':'National Highway Traffic Safety Administration',
		'FHWA':'Federal HighwayAdministration',
		'FTA':'Federal Transit Administration',
		'WAPA':'Western Area Power Administration',
		'NMFS':'National Marine Fisheries Services ',
		'NRCS':'Natural Resources Conservation Service',
		'APHIS':'Animal and Plant Inspection Service',
		'BLM':'Bureau of Land Management',
		'NOAA':'National Oceanic and Atmospheric Administration',
		'WAP':'',
		'HHS':'Department of Health and Human Services',
		'NIH':'National Institutes of Health',
		'USACE':'US Army Corps of Engineers',
		'USFWS':'Us Fish and Wildlife Service',
		'USFS':'US Forrest Service',
		'NRC':'Nuclear Regulatory Commission',
		'USPS':'US Postal Service',
		'NASA':'National Aeronautics and Space Administration',
		'RUS':'',
		'NPS':''
}

agencies_abbrev_list = [
	'AFS', 'APHIS', 'BIA', 'BLM', 'BOEM', 'BPA', 'BR', 'DOC', 'DOE', 'DOI', 
	'DOS', 'DOT', 'EPA', 'FAA', 'FERC', 'FHWA', 'FRA', 'FSA', 'FTA', 'GSA', 
	'HHS', 'HUD', 'NASA', 'NHTSA', 'NIH', 'NMFS', 'NNSA', 'NOAA', 'NPS', 'NRC', 
	'NRCS', 'NSF', 'OSM', 'RUS', 'STB', 'USA', 'USACE', 'USAF', 'USCG', 'USDA', 
	'USFS', 'USFWS', 'USMC', 'USN', 'USPS', 'VA', 'WAP', 'WAPA']


class Search(object):
	def search(self, search_params):
		body={
		    "query": {
		        "bool":{
		            "must": [],
		            "should": [
		                {
		                    "match": {
		                        "title": {
		                            "query": search_params['query'], 
		                            "fuzziness": "AUTO",
		                            "minimum_should_match":"75%",
		                            "boost":10
		                        }
		                    }
		                }, {
		                    "has_child": {
		                        "type":"eis_file",
		                        "score_mode":"max",
		                        "query": {
		                            "match":{
		                                "file": {
		                                    "query":search_params['query'],
		                                    "fuzziness": "AUTO",
		                                    "minimum_should_match":"90%",
		                                    "boost":1
		                                }
		                            }
		                        }
		                    }
		                }
		            ]
		        }
		    }
		}
		if search_params['state']:
		    body['query']['bool']['must'].append(
		    	{"term": {"state_abbrev":search_params['state']}})
		if search_params['agency']:
		    body['query']['bool']['must'].append(
		    	{"term": {"agency_abbrev":search_params['agency']}})
		if search_params['date_from'] and search_params['date_to']:
		    body['query']['bool']['must'].append(
		        {"range": {"date": {
		        	"gte":search_params['date_from'], 
		        	"lte":search_params['date_to']}}})
		elif search_params['date_from']:
		    body['query']['bool']['must'].append(
		        {"range": {"date": {
		        	"gte":search_params['date_from'], 
		        	"lte":"2020-01-01"}}})
		elif search_params['date_to']:
		    body['query']['bool']['must'].append(
		        {"range": {"date": {
		        	"gte":"1900-01-01", 
		        	"lte":search_params['date_to']}}})
		if search_params['final_eis_only'] == 'on':
		    body['query']['bool']['must'].append(
		    	{"term": {"document_type":"final"}})
		logging.info(body['query']['bool']['must'])
		res = es.search(
		    index="impactstatement", 
		    doc_type="report",
		    fields = ['title', 'state_abbrev', 'agency_abbrev', 
		    	'date', 'eis_number', "document_type"],
			body=body, 
		    ignore=[400, 404], 
		    from_=search_params["display_from"], 
		    size=search_params['display_num'])
		res['hits']['hits']
		return {
				"hits":res['hits']['hits'], 
				"total_hits":res['hits']['total']
			}

	def advancedSearch(self, query, from_, size):
		query.replace(" and ", " AND ")
		res = es.search(
			index='eistxt',

			fields=["file_url", "eis", "title"], 
			body={
		      "query" : {
		        "match" : {
		          "file" : query
		        }
		      },
		      "highlight" : {
		        "fields" : {
		          "file" : {}
		        }
		      },
		    "from":0,
		    "size":50
		}, 
		ignore=[400, 404], from_=from_, size=size)
		return {
				"hits":res['hits']['hits'], 
				"total_hits":res['hits']['total']
			}

class Tools(object):
	def pack_search_results(self, results):
		eis = list(set([r['fields']['eis'][0] for r in results]))
		reports = models.Report.objects(__raw__={
						'eis_number': {
							'$in': eis
						}
					}).only('title',
					'eis_number')
		titles = {}
		for r in reports:
		    titles[r.eis_number] = r.title
		reports = []
		for r in results:
		    reports.append({
		        "title": titles[r['fields']['eis'][0]],
		        "file_title": r['fields']['title'][0],
		        "eis":r['fields']['eis'][0],
		        "highlights": [h.replace("<em>","<strong>").replace("</em>", "</strong>") for h in r['highlight']['file']]
		    })
		return reports


