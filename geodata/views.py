import json 
from django.http import HttpResponse
from django.db import connection
from surveys.models import Survey

from itertools import groupby 
import re
import pandas as pd

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

get_agreed = lambda x, d: 1 if re.match(r'agree',KEY.get(d.get(x,''),'')) else 0

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

def add_fillkey(output):
	''' add a fillkey attribute for top response '''
	for s in output:
		m = max(output[s].values())
		v = sorted([ k for k in output[s] if output[s][k]==m])
		if 'stronglyAgree' in v:
			output[s]['fillKey'] = 'stronglyAgree'
		elif 'agree' in v:
			output[s]['fillKey'] = 'agree'
		elif 'somewhatAgree' in v:
			output[s]['fillKey'] = 'somewhatAgree'
		elif 'neitherAgreeNorDisagree' in v:
			output[s]['fillKey'] = 'neitherAgreeNorDisagree'
		elif 'somewhatDisagree' in v:
			output[s]['fillKey'] = 'somewhatDisagree'
		elif 'disagree' in v:
			output[s]['fillKey'] = 'disagree'
		elif 'stronglyDisagree' in v:
			output[s]['fillKey'] = 'stronglyDisagree'
		elif 'refused' in v:
			output[s]['fillKey'] = 'refused'
		else:
			output[s]['fillKey'] = 'unknown'
	return output

def get_geodata(question):
	output = {}
	question = str(question)
        if question == '1':
                matches = sorted([
                        (str(m.state)
                        , KEY[DPES11_DICT[int(float(m.i_develop_strong_emotions_toward_people_i_can_rely_on))]])
                        for m in Survey.objects.all()
                ])
        elif question == '2':
                matches = sorted([
                        (str(m.state)
                        , KEY[DPES11_DICT[int(float(m.parents_should_empower_children_as_much_as_possible_so_that_they_may_follow_their_dreams))]])
                        for m in Survey.objects.all()
                ])
        elif question == '3':
                matches = sorted([
                        (str(m.state)
                        , KEY[EPQ1_DICT[int(float(m.moral_standards_should_be_seen_as_individualistic_what_one_person_considers_to_be_moral_may_be_judged_as_immoral_by_another_person))]])
                        for m in Survey.objects.all()
                ])
        elif question == '4':
                matches = sorted([
                        (str(m.state)
                        , KEY[IS6_DICT[int(float(m.if_one_believes_something_is_right_one_must_stand_by_it_even_if_it_means_losing_friends_or_missing_out_on_profitable_opportunities))]])
                        for m in Survey.objects.all()
                ])
        elif question == '5':
                matches = sorted([
                        (str(m.state)
                        , KEY[I10_DICT[int(float(m.spiritually_i_consider_myself))]])
                        for m in Survey.objects.all()
                ])
        else:
                raise Exception('Question needs to be 1-5')
        output = do_grouping(matches)
        # output = add_fillkey(output)
	return output

def get_geodata_scores(question):
	output = {}
	question = str(question)
	if question == '1':
		matches = sorted([
			   (str(m.state)
			    , get_agreed(int(float(m.i_develop_strong_emotions_toward_people_i_can_rely_on))	
				, DPES11_DICT)
			       # * float(m.weight) 
			   )
			   for m in Survey.objects.all() ])
	elif question == '2':
		matches = sorted([
                           (str(m.state)
                            , get_agreed(int(float(m.parents_should_empower_children_as_much_as_possible_so_that_they_may_follow_their_dreams)), DPES11_DICT)
			      # * float(m.weight) 
			   )
                           for m in Survey.objects.all() ])
	elif question == '3':
		matches = sorted([
                           (str(m.state)
                            , get_agreed(int(float(m.moral_standards_should_be_seen_as_individualistic_what_one_person_considers_to_be_moral_may_be_judged_as_immoral_by_another_person)), EPQ1_DICT)
			      # * float(m.weight) 
			   )
                           for m in Survey.objects.all() ])
	elif question == '4':
		matches = sorted([
                           (str(m.state)
                            , get_agreed(int(float(m.if_one_believes_something_is_right_one_must_stand_by_it_even_if_it_means_losing_friends_or_missing_out_on_profitable_opportunities)), IS6_DICT)
			       # * float(m.weight) 
			   )
                           for m in Survey.objects.all() ])
	elif question == '5':
		matches = sorted([
                           (str(m.state)
                            , get_agreed(int(float(m.spiritually_i_consider_myself)), I10_DICT)
			       # * float(m.weight) 
			   )
                           for m in Survey.objects.all() ])
	else:
		raise Exception('Question needs to be 1-5')
	output = do_calculation(matches)
	groupings = get_geodata(question)
	for i, s in enumerate(output):
		d = groupings[s['abbr']]
		output[i].update(d)
	return output

def get_fillkey():
	colors = {
		'sa':'#2BC0E8'
		, 'a':'#3780E8'
		, 'swa':'#4573E8'
		, 'nad':'#7893E8'
		, 'swd':'#A57FE8'
		, 'd':'#8D39E8'
		, 'sd':'#F448FF'
		, 'r':'#B6B6B4'
		, 'def':'#B6B6B4'
	}
	FILLKEY = '''
	  'stronglyAgree': '{sa}',
	  'agree': '{a}',
	  'somewhatAgree': '{swa}',
	  'neitherAgreeNorDisagree': '{nad}',
	  'somewhatDisagree': '{swd}',
	  'disagree': '{d}',
	  'stronglyDisagree': '{sd}',
	  'refused ': '{r}',
	  defaultFill: '{def}'
	'''.format(**colors)
	return FILLKEY

def get_sortbar_by_regions(sql):
	results = pd.read_sql(sql, connection)
        results['concat'] = results['region']+': '+results['gender']
        #  {'Category':'West: Male','Weighted_Pct':'0.373072187'},
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

