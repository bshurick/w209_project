import json 
from django.http import HttpResponse
from django.db import connection
from surveys.models import Survey

from itertools import groupby 
import re
import pandas as pd
import numpy as np

REGIONS = {'AK': 'West',
 'AL': 'South',
 'AR': 'South',
 'AZ': 'West',
 'CA': 'West',
 'CO': 'West',
 'CT': 'Northeast',
 'DC': 'South',
 'DE': 'South',
 'FL': 'South',
 'GA': 'South',
 'HI': 'West',
 'IA': 'Midwest',
 'ID': 'West',
 'IL': 'Midwest',
 'IN': 'Midwest',
 'KS': 'Midwest',
 'KY': 'South',
 'LA': 'South',
 'MA': 'Northeast',
 'MD': 'South',
 'ME': 'Northeast',
 'MI': 'Midwest',
 'MN': 'Midwest',
 'MO': 'Midwest',
 'MS': 'South',
 'MT': 'West',
 'NC': 'South',
 'ND': 'Midwest',
 'NE': 'Midwest',
 'NH': 'Northeast',
 'NJ': 'Northeast',
 'NM': 'West',
 'NV': 'West',
 'NY': 'Northeast',
 'OH': 'Midwest',
 'OK': 'South',
 'OR': 'West',
 'PA': 'Northeast',
 'RI': 'Northeast',
 'SC': 'South',
 'SD': 'Midwest',
 'TN': 'South',
 'TX': 'South',
 'UT': 'West',
 'VA': 'South',
 'VT': 'Northeast',
 'WA': 'West',
 'WI': 'Midwest',
 'WV': 'South',
 'WY': 'West'}

STATES = {u'AK': u'Alaska',
 u'AL': u'Alabama',
 u'AR': u'Arkansas',
 u'AS': u'American Samoa',
 u'AZ': u'Arizona',
 u'CA': u'California',
 u'CO': u'Colorado',
 u'CT': u'Connecticut',
 u'DC': u'District of Columbia',
 u'DE': u'Delaware',
 u'DK': u'Dakota',
 u'FL': u'Florida',
 u'GA': u'Georgia',
 u'GU': u'Guam',
 u'HI': u'Hawaii',
 u'IA': u'Iowa',
 u'ID': u'Idaho',
 u'IL': u'Illinois',
 u'IN': u'Indiana',
 u'KS': u'Kansas',
 u'KY': u'Kentucky',
 u'LA': u'Louisiana',
 u'MA': u'Massachusetts',
 u'MD': u'Maryland',
 u'ME': u'Maine',
 u'MI': u'Michigan',
 u'MN': u'Minnesota',
 u'MO': u'Missouri',
 u'MP': u'Northern Mariana Islands',
 u'MS': u'Mississippi',
 u'MT': u'Montana',
 u'NC': u'North Carolina',
 u'ND': u'North Dakota',
 u'NE': u'Nebraska',
 u'NH': u'New Hampshire',
 u'NJ': u'New Jersey',
 u'NM': u'New Mexico',
 u'NV': u'Nevada',
 u'NY': u'New York',
 u'OH': u'Ohio',
 u'OK': u'Oklahoma',
 u'OL': u'Orleans',
 u'OR': u'Oregon',
 u'PA': u'Pennsylvania',
 u'PI': u'Philippine Islands',
 u'PR': u'Puerto Rico',
 u'RI': u'Rhode Island',
 u'SC': u'South Carolina',
 u'SD': u'South Dakota',
 u'TN': u'Tennessee',
 u'TX': u'Texas',
 u'UT': u'Utah',
 u'VA': u'Virginia',
 u'VI': u'Virgin Islands',
 u'VT': u'Vermont',
 u'WA': u'Washington',
 u'WI': u'Wisconsin',
 u'WV': u'West Virginia',
 u'WY': u'Wyoming'}

DPES11_DICT = {-1:'Refused'
                ,1: 'Strongly disagree'
                ,2: 'Disagree'
                ,3: 'Somewhat disagree'
                ,4: 'Neither agree nor disagree'
                ,5: 'Somewhat agree'
                ,6: 'Agree'
                ,7: 'Strongly agree'}

EPQ1_DICT = {-1:'Refused'
                ,1: 'Strongly agree'
                ,2: 'Agree'
                ,3: 'Somewhat agree'
                ,4: 'Neither agree nor disagree'             
                ,5: 'Somewhat disagree'
                ,6: 'Disagree'
                ,7: 'Strongly disagree'}

IS6_DICT = {
    -1:'Refused'
    , 1:'Strongly disagree'
    , 2:'Disagree'
    , 3:'Neither agree nor disagree'
    , 4:'Agree'
    , 5:'Strongly agree'
}

I10_DICT = {
    -1:'Refused'
    , 1:'Very spiritual'
    , 2:'Spiritual'
    , 3:'Somewhat spiritual'
    , 4:'Not spiritual'
    , 5:'Anti-spiritual'
}

QUESTION = {
	'1':DPES11_DICT
	,'2':DPES11_DICT
	,'3':EPQ1_DICT
	,'4':IS6_DICT
	,'5':I10_DICT
}

REVERSE = {
	-1:-1
	, 7:1
	, 6:2
 	, 5:3
	, 4:4
	, 3:5
	, 2:6
	, 1:7
}

KEY = {
    'Strongly agree':'agree'
   , 'Agree':'agree'
   , 'Somewhat agree':'agree'
   , 'Neither agree nor disagree':'neitherAgreeNorDisagree'
   , 'Somewhat disagree':'disagree'
   , 'Disagree':'disagree'
   , 'Strongly disagree':'disagree'
   , 'Refused':'refused'
   , 'Somewhat spiritual':'agree'
   , 'Very spiritual':'agree'
   , 'Spiritual':'agree'
   , 'Not spiritual':'disagree'
   , 'Anti-spiritual':'disagree'
}

@np.vectorize
def get_response_key(x, q):
	key = QUESTION[q]
	answer = key[int(float(x))]
	return KEY[answer]

def do_grouping(matches):
	''' group together responses for each state '''
	output = {}
	groups = [ (k[0],list(g)) for k, g in groupby(matches) ]
	for g in groups:
	    if g[0] not in output:
		output[g[0]] = {}
	    for v in g[1]:
		if v[1] not in output[g[0]]:
		    output[g[0]][v[1]] = 0 
		output[g[0]][v[1]] += 1
	return output

def do_calculation(matches):
	''' sum together responses and take average '''
	scores = {}; output = {}
	groups = [ (k[0],list(g)) for k, g in groupby(matches) ]
	for g in groups:
	    if g[0] not in scores:
		scores[g[0]] = {}
	    for v in g[1]:
		if v[1] not in scores[g[0]]:
		    scores[g[0]][v[1]] = 0
	        scores[g[0]][v[1]] += 1.0
	for state in scores:
	    cnt = sum(scores[state].values())
	    output[state] = round(sum(x*y for x,y in scores[state].iteritems())*1.0/cnt,4) \
				if cnt > 0 else 0.0
	return [
		{
		 'state':str(STATES[s])
		 ,'abbr':str(s)
		 ,'score':v
		} 
		for s,v in output.iteritems()
	]

def geodata_sql(question):
	if question == '1':
		field = 'strong_emotions'
	elif question == '2':
		field = 'empower_children'
	elif question == '3':
		field = 'individualistic_morals'
	elif question == '4':
		field = 'losing_friends'
	elif question == '5':
		field = 'spirituality'
	sql = '''
		select 
		state
		, {} field
		, sum(weight) count 
		from surveys_survey
		group by 1,2
		;
	'''.format(field)
	return sql

def geodata_format(results, q):
	output = []
	results['key'] = get_response_key(results['field'], q)
	results = results[['key','state','count']].groupby(['key','state']).sum()	
	results = results.reset_index(level=0).reset_index(level=0)
	keys = set(results['key'])
	states = set(map(lambda x: str(x), results['state'].values))
	for s in states:
		kout = {}
		state = results['state']==s
		key_agree = (results['key']=='agree') & (state)
		kout['abbr'] = str(results.loc[state,'state'].values[0])
		kout['state'] = str(STATES[kout['abbr']])
		kout['score'] = np.sum(results.loc[key_agree,'count'])*1.0/np.sum(results.loc[state,'count'])
		for k in keys:
			key_state = (results['key']==k) & (state)
			if len(results.loc[key_state,'count'])>1: raise Exception('Check data')
			if np.sum(key_state)>0:
				kout[k] = int(results.loc[key_state,'count'].iloc[0])
			else:
				kout[k] = 0
			output.append(kout)
	return output

def get_geodata_scores(question):
	output = {}
	question = str(question)
	matches = pd.read_sql(geodata_sql(question), connection)
	output = geodata_format(matches, question)
	return output

def get_sortbar_by_regions(sql):
	results = pd.read_sql(sql, connection)
        results['concat'] = results['region']+': '+results['gender']
        output = [ {'Category':str(s),'Weighted_Pct':str(r)}
                    for s,r in zip(results['concat'],results['result']) ]
	return output

def get_question_by_regions(sql):
	regions = ['Midwest', 'Northeast', 'South', 'West']
	results = pd.read_sql(sql, connection)
	female = []
	male = []
	for r in regions:
    	    female.append(results.loc[(results['region']==r) & (results['gender']=='Female'),'result' ].iloc[0])
    	    male.append(results.loc[(results['region']==r) & (results['gender']=='Male'),'result' ].iloc[0])
	out = { 'labels':regions, 'series':[{'label':'Female', 'values':female},{'label':'Male', 'values':male} ]}
	return out

def get_spirituality_by_region(sortbar=False):
	sql = '''
		select 
		region
		,gender
		,sum(weight*case when cast(spirituality as integer) in (1,2) 
			then 1 else 0 end)
		/sum(weight) result 
		from surveys_survey 
		group by 1,2
		order by 3 desc;
	'''
	if sortbar:
		return get_sortbar_by_regions(sql)
	else:
		return get_question_by_regions(sql)

def get_q1_agree_byregion(sortbar=False):
	sql = '''
                select
                gender
                , region
                , sum(weight*case when cast(strong_emotions as integer) in (5,6,7)
                        then 1 else 0 end)/sum(weight) result
                from surveys_survey
                group by 1,2
                order by 3 desc;
        '''
	if sortbar:
		return get_sortbar_by_regions(sql)
	else:
		return get_question_by_regions(sql)

def get_q2_agree_byregion(sortbar=False):
        sql = '''
                select
                gender
                , region
                , sum(weight*case when cast(empower_children as integer) in (5,6,7)
                        then 1 else 0 end)/sum(weight) result
                from surveys_survey
                group by 1,2
                order by 3 desc;
        '''
	if sortbar:
		return get_sortbar_by_regions(sql)
	else:
		return get_question_by_regions(sql)

def get_q3_agree_byregion(sortbar=False):
        sql = '''
                select
                gender
                , region
                , sum(weight*case when cast(individualistic_morals as integer) in (1,2,3)
                        then 1 else 0 end)/sum(weight) result
                from surveys_survey
                group by 1,2
                order by 3 desc;
        '''
	if sortbar:
		return get_sortbar_by_regions(sql)
	else:
		return get_question_by_regions(sql)

def get_q4_agree_byregion(sortbar=False):
        sql = '''
                select
                gender
                , region
                , sum(weight*case when cast(losing_friends as integer) in (4,5)
                        then 1 else 0 end)/sum(weight) result
                from surveys_survey
                group by 1,2
                order by 3 desc;
        '''
	if sortbar:
		return get_sortbar_by_regions(sql)
	else:
		return get_question_by_regions(sql)

def geodata(request):
	question = request.GET.get('question')
	output = get_geodata(question)
	return HttpResponse(json.dumps(output),content_type='application/json')

