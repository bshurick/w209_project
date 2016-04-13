from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader

from .models import Survey
from .forms import SurveyForm
from geodata.views import REGIONS 

def survey(request):
	if request.method == 'POST':
		# edit the post data
		postdata = request.POST.copy()
		
		# which video did they watch	
		video = request.session.get('video')
		postdata['video_choice'] = video
	
		# which region are they from	
		state = postdata['state']
		region = REGIONS.get(state, 'Unknown')
		postdata['region'] = region
		
		# save data if valid
		f = SurveyForm(postdata)
		if f.is_valid():
			f.save()
			request.session['watched_video'] = True
			return HttpResponseRedirect('/')
	else:
		f = SurveyForm()
	tmp = loader.get_template('survey_form.html')
	return HttpResponse(tmp.render({'form':f}, request))


