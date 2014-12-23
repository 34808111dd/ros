'''
Created on Dec 19, 2014

@author: Coeurl
'''


from processor.shortcuts import request_type
from django.shortcuts import HttpResponseRedirect

#===============================================================================
# Utility requests
#===============================================================================

@request_type('GET', False)
def set_language(request):
    '''
    Set language cookie, redirect to requested page
    '''
    lang = request.GET.get('lang', None)
    response = HttpResponseRedirect(request.META["HTTP_REFERER"])
    if lang == "ru":
        response.set_cookie(key="lang", value="ru", max_age=365*24*60*60, expires=None, path='/')
    else:
        response.set_cookie(key="lang", value="en", max_age=365*24*60*60, expires=None, path='/')
    return response

