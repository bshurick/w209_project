from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

import random, requests
from geodata.views import \
	  get_geodata_scores \
	, get_spirituality_by_region \
	, get_q1_agree_byregion \
	, get_q2_agree_byregion \
	, get_q3_agree_byregion \
	, get_q4_agree_byregion \
	, get_video_responses

def index(request):
	videos = {
		'control':'https://www.youtube.com/embed/2DN0IRoMf4k'
		,'test':'https://www.youtube.com/embed/V6-0kYhqoRo'
	}
	if not request.session.get('video'):
		r = int(random.random()*10000)
		if r % 2 == 0:
			video = videos['control']
			request.session['video'] = 'control'
		else:
			video = videos['test']
			request.session['video'] = 'test'
	else:
		video = videos[request.session.get('video')]
	tmp = loader.get_template('index.html')
	watched_video = request.session.get('watched_video',False)
	nfilter=10
	q1_question = 'I develop strong emotions toward people who I can rely on'
	q2_question = 'Parents should empower children as much as possible so that they may follow their dreams'
	q3_question = 'Moral standards should be seen as individualistic -- what one person considers to be moral may be judged as immoral by another person'
	q4_question = 'If one believes something is right one must stand by it, even if it means losing friends or missing out on profitable opportunities'
	q5_question = 'I consider myself spiritual, somewhat spiritual, or very spiritual'
	mapchart_title = 'Agreement, by state'
	mapchart_title_subtext = 'Map of % in agreement to the question'
	scatter_title = 'Percent agree vs. disagree, state scatterplot'
	scatter_subtext = 'States in the upper-left quadrant more often disagree, while states in the lower-right quadrant more often agree with the question.'
	sortbar_title = 'Percent agreed, gender and region'
	c = {
		'video':video
		,'watched_video':watched_video
		,'video_responses':get_video_responses()
		,'nfilter':nfilter
		,'q1_scores':get_geodata_scores(1)
		,'q2_scores':get_geodata_scores(2)
		,'q3_scores':get_geodata_scores(3)
		,'q4_scores':get_geodata_scores(4)
		,'q5_scores':get_geodata_scores(5)
		,'q1_scores_filter':get_geodata_scores(1,nfilter)
		,'q2_scores_filter':get_geodata_scores(2,nfilter)
		,'q3_scores_filter':get_geodata_scores(3,nfilter)
		,'q4_scores_filter':get_geodata_scores(4,nfilter)
		,'q5_scores_filter':get_geodata_scores(5,nfilter)
		,'q1_bar':get_q1_agree_byregion()
		,'q2_bar':get_q2_agree_byregion()
		,'q3_bar':get_q3_agree_byregion()
		,'q4_bar':get_q4_agree_byregion()
		,'q5_bar':get_spirituality_by_region()
		,'q1_sortbar':get_q1_agree_byregion(sortbar=True)
		,'q2_sortbar':get_q2_agree_byregion(sortbar=True)
		,'q3_sortbar':get_q3_agree_byregion(sortbar=True)
		,'q4_sortbar':get_q4_agree_byregion(sortbar=True)
		,'q5_sortbar':get_spirituality_by_region(sortbar=True)
		,'mapchart_title':mapchart_title
		,'scatter_title':scatter_title
		,'scatter_subtext':scatter_subtext
		,'sortbar_title':sortbar_title
		,'q1_question':q1_question
		,'q2_question':q2_question
		,'q3_question':q3_question
		,'q4_question':q4_question
		,'q5_question':q5_question
	}
	return HttpResponse(tmp.render(c,request))



