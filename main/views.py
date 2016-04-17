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
	}
	return HttpResponse(tmp.render(c,request))



