import json 
from django.http import HttpResponse
from surveys.models import Survey
from itertools import groupby 

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
    'Strongly agree':'stronglyAgree'
   , 'Agree':'agree'
   , 'Somewhat agree':'somewhatAgree'
   , 'Neither agree nor disagree':'neitherAgreeNorDisagree'
   , 'Somewhat disagree':'somewhatDisagree'
   , 'Disagree':'disagree'
   , 'Strongly disagree':'stronglyDisagree'
   , 'Refused':'refused'
}

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
		if v[1]>0:
		    if v[1] not in scores:
		        scores[g[0]][v[1]] = 0
	            scores[g[0]][v[1]] += 1
	for state in scores:
	    output[state] = round(sum(x*y for x,y in scores[state].iteritems())*1.0/sum(scores[state].values()),4)
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
        else:
                raise Exception('Question needs to be 1-3')
        output = do_grouping(matches)
        # output = add_fillkey(output)
	return output

def get_geodata_scores(question):
	output = {}
	question = str(question)
	if question == '1':
		matches = sorted([
			   (str(m.state)
			    , int(float(m.i_develop_strong_emotions_toward_people_i_can_rely_on)))
			   for m in Survey.objects.all() ])
	elif question == '2':
		matches = sorted([
                           (str(m.state)
                            , int(float(m.parents_should_empower_children_as_much_as_possible_so_that_they_may_follow_their_dreams)))
                           for m in Survey.objects.all() ])
	elif question == '3':
		matches = sorted([
                           (str(m.state)
                            , REVERSE[int(float(m.moral_standards_should_be_seen_as_individualistic_what_one_person_considers_to_be_moral_may_be_judged_as_immoral_by_another_person))])
                           for m in Survey.objects.all() ])
	else:
		raise Exception('Question needs to be 1-3')
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

def geodata(request):
	question = request.GET.get('question')
	output = get_geodata(question)
	return HttpResponse(json.dumps(output),content_type='application/json')

