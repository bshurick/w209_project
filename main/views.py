from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

import random, requests
from geodata.views import \
	  get_geodata_scores \
	, get_spirituality_by_region

def index(request):
	videos = {
		'test':'https://www.youtube.com/embed/2DN0IRoMf4k'
		,'control':'https://www.youtube.com/embed/V6-0kYhqoRo'
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
	c = {
		'video':video
		,'watched_video':watched_video
		,'q1_scores':get_geodata_scores(1)
		,'q2_scores':get_geodata_scores(2)
		,'q3_scores':get_geodata_scores(3)
		,'q5_sortbar':get_spirituality_by_region()
	}
	return HttpResponse(tmp.render(c,request))



