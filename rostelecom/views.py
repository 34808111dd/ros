#from django.http import HttpResponse
#from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

def home(request):
    return HttpResponseRedirect("/rnr/")
