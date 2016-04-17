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

INCOME = {-2:'Not asked',-1:'REFUSED'
            ,1 :'<$5,000'
            ,2 :'$5,000 to $7,499'
            ,3 :'$7,500 to $9,999'
            ,4 :'$10,000 to $12,499'
            ,5 :'$12,500 to $14,999'
            ,6 :'$15,000 to $19,999'
            ,7 :'$20,000 to $24,999'
            ,8 :'$25,000 to $29,999'
            ,9 :'$30,000 to $34,999'
            ,10: '$35,000 to $39,999'
            ,11: '$40,000 to $49,999'
            ,12: '$50,000 to $59,999'
            ,13: '$60,000 to $74,999'
            ,14: '$75,000 to $84,999'
            ,15: '$85,000 to $99,999'
            ,16: '$100,000 to $124,999'
            ,17: '$125,000 to $149,999'
            ,18: '$150,000 to $174,999'
            ,19: '>=$175,000'}

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

VID = {-1:'Not Answered'
	, 1:'Weekly'
	, 2:'Monthly'
	, 3:'Few Times Yearly'
	, 4:'Never'
	, 5:'Not Applicable'}

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

def geodata_format(results, q, nfilter=0):
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
		key_disagree = (results['key']=='disagree') & (state)
		kout['abbr'] = str(results.loc[state,'state'].values[0])
		kout['state'] = str(STATES[kout['abbr']])
		d = results.loc[key_disagree,'count'].apply(lambda x: round(x))
		a = results.loc[key_agree,'count'].apply(lambda x: round(x))
		t = results.loc[state,'count'].apply(lambda x: round(x))
		kout['disagree_score'] = np.sum(d)*1.0/np.sum(t)
		kout['score'] = np.sum(a)*1.0/np.sum(t)
		kout['total'] = np.sum(t)
		
		# loop through keys
		for k in keys:
			key_state = (results['key']==k) & (state)
			if len(results.loc[key_state,'count'])>1: raise Exception('Check data')
			if np.sum(key_state)>0:
				kout[k] = int(round(results.loc[key_state,'count'].iloc[0]))
			else:
				kout[k] = 0
		
		# append state values
		if kout['total']>nfilter:
			output.append(kout)
	return output

def get_geodata_scores(question, nfilter=0):
	output = {}
	question = str(question)
	matches = pd.read_sql(geodata_sql(question), connection)
	output = geodata_format(matches, question, nfilter)
	return output

def get_sortbar_by_regions(sql):
	results = pd.read_sql(sql, connection)
        results['concat'] = results['region']+': '+results['gender']
        output = [ {'Category':str(s),'Weighted_Pct':str(r), 'Sorted':str(s)}
                    for s,r in zip(results['concat'],results['result']) ]
	return output

def get_sortbar_by_income(sql):
	results = pd.read_sql(sql, connection)
	results['income_str'] = results['income'].apply(lambda x: INCOME[int(x) if len(str(x))>0 and x else -2])
	output = [ {'Category':str(s),'Weighted_Pct':str(r), 'Sorted':i}
                    for i,s,r in sorted(zip(results['income'],results['income_str'],results['result']), key=lambda x: x[0]) ]
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

def get_question_by_video(sql):
	choices = ['Weekly','Monthly','Few Times Yearly','Never','Not Applicable']
	results = pd.read_sql(sql, connection)
	results['choices'] = results['call_parents'].apply(lambda x: VID[int(x if x else -1)])
	results['video_choice'] = results['video_choice'].apply(lambda x: x if len(str(x))>0 else 'None')
	test = []
	control = []
	for c in choices:	
	    test_result = results.loc[(results['choices']==c) & (results['video_choice']=='test'),'result']
	    control_result = results.loc[(results['choices']==c) & (results['video_choice']=='control'),'result']
	    test.append(test_result.iloc[0] if test_result.shape[0]>0 else 0)
	    control.append(control_result.iloc[0] if control_result.shape[0]>0 else 0)
	out = { 'labels':choices, 'series':[{'label':'Family Video', 'values':test}, \
						     {'label':'Honda Video', 'values':control }]}
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

def get_q1_agree_byincome(sortbar=True):
	sql = '''
		select 
		cast(coalesce(case when income='' then '-2' else income end,'-2') as integer) income
		, sum(weight*case when cast(strong_emotions as integer) in (5,6,7)
                        then 1 else 0 end)/sum(weight) result
		from surveys_survey
		group by 1
		order by 1	
	'''	
	return get_sortbar_by_income(sql)

def get_q2_agree_byincome(sortbar=True):
	sql = '''
		select 
		cast(coalesce(income,'-2') as integer) income
		, sum(weight*case when 
			cast(empower_children as integer) in (5,6,7)
                        then 1 else 0 end)/sum(weight) result
		from surveys_survey
		group by 1
		order by 1	
	'''	
	return get_sortbar_by_income(sql)

def get_q3_agree_byincome(sortbar=True):
	sql = '''
		select 
		cast(coalesce(income,'-2') as integer) income
		, sum(weight*case when 
			cast(individualistic_morals as integer) in (1,2,3)
                        then 1 else 0 end)/sum(weight) result
		from surveys_survey
		group by 1
		order by 1	
	'''	
	return get_sortbar_by_income(sql)

def get_q4_agree_byincome(sortbar=True):
	sql = '''
		select 
		cast(coalesce(income,'-2') as integer) income
		, sum(weight*case when 
			cast(losing_friends as integer) in (4,5)
                        then 1 else 0 end)/sum(weight) result
		from surveys_survey
		group by 1
		order by 1	
	'''	
	return get_sortbar_by_income(sql)

def get_q5_agree_byincome(sortbar=True):
	sql = '''
		select 
		cast(coalesce(income,'-2') as integer) income
		, sum(weight*case when 
			cast(spirituality as integer) in (1,2)
                        then 1 else 0 end)/sum(weight) result
		from surveys_survey
		group by 1
		order by 1	
	'''	
	return get_sortbar_by_income(sql)

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

def get_video_responses():
	sql = '''
		select
		video_choice
		, call_parents
		, count(*) result 
		from surveys_survey
		group by 1,2
		order by 1,2 ;
	'''
	return get_question_by_video(sql)

def geodata(request):
	question = request.GET.get('question')
	output = get_geodata(question)
	return HttpResponse(json.dumps(output),content_type='application/json')

