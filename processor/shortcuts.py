'''
Created on Dec 19, 2014

@author: Coeurl

Shortcuts for:

'''
from django.http import HttpResponseBadRequest, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client
from Cookie import SimpleCookie
import simplejson

success_response = simplejson.dumps({'success':True,'error':[]})
unsuccess_response = simplejson.dumps({'success':False,'error':[]})

class request_type():
    '''
    If request does not match, return standard 400 error
    '''
    def __init__(self, request_type, is_ajax):
        self.request_type = request_type
        self.is_ajax = is_ajax
        
    def __call__(self, func):
        def wrapper(request, *args):
            if request.method == self.request_type and self.is_ajax == request.is_ajax():
                return func(request)
            else:
                return HttpResponseBadRequest()
        return wrapper



class lang_aware():
    '''
    Check if client has cookie with language,
    set it if has not, pass language to view function
    '''
    def __init__(self, template_lang_dict):
        self.template_lang_dict = template_lang_dict
        
    def __call__(self, func):
        
        def wrapper(request, *args):
            lang = request.COOKIES.get('lang', None)
            if lang == 'ru':
                return func(request, self.template_lang_dict['ru'])
            if lang == 'en':
                return func(request, self.template_lang_dict['en'])
            else:
                response=func(request, self.template_lang_dict['ru'])
                response.set_cookie(key="lang", value="en", max_age=365*24*60*60, expires=None, path='/')
                return response
        return wrapper


def http400onError(func):
    '''
    Return Http 400 on any error, Http404 if object not found
    '''
    def wrapper(*args, **kargs):
        try:
            return func(*args, **kargs)
        except ObjectDoesNotExist:
            raise Http404
        except Exception:
            return HttpResponseBadRequest()
    return wrapper



def http_request(url, method='get', ajax=True, content_type = 'application/json', data=dict(), cookie = dict()):
    cl = Client()
    request = cl.get if method == 'get' else cl.post
    if cookie:
        _c = SimpleCookie()
        for k, v in cookie.items():
            _c[k] = v
        cl.cookies=_c
    #print 'data requested:',data
    if ajax:
        if content_type:
            response = request(url, data=data, content_type=content_type, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        else:
            response = request(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    else:
        if content_type:
            response = request(url, data=data, content_type=content_type)
        else:
            response = request(url, data=data)
    return response