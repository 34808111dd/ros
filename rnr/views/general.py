'''
Created on Dec 19, 2014

@author: Coeurl
'''

from processor.shortcuts import request_type, lang_aware
from django.shortcuts import render_to_response
from django.utils import timezone

#===============================================================================
# templates for general requests
#===============================================================================

rnr_home_templates = {'en':'en/rnr_home_en.html', 'ru':'ru/rnr_home_ru.html'}
rnr_works_telmpates = {'en':'en/rnr_works_en.html', 'ru':'ru/rnr_works_ru.html'}
rnr_notifications_telmpates = {'en':'en/rnr_notifications_en.html', 'ru':'ru/rnr_notifications_ru.html'}
rnr_clients_telmpates = {'en':'en/rnr_clients_en.html', 'ru':'ru/rnr_clients_ru.html'}
rnr_dictionary_templates = {'en':'en/rnr_dictionary_en.html', 'ru':'ru/rnr_dictionary_ru.html'}
rnr_about_templates = {'en':'en/rnr_about_en.html', 'ru':'ru/rnr_about_ru.html'}

#===============================================================================
# Timezones
#===============================================================================
local_tz = timezone.get_current_timezone()
utc_tz = timezone.utc


#===============================================================================
# General requests
#===============================================================================

@request_type('GET', False)
@lang_aware(rnr_home_templates)
def rnr_home(request, template_name):
    '''/rnr/'''
    return render_to_response(template_name)

@request_type('GET', False)
@lang_aware(rnr_works_telmpates)
def rnr_works(request, template_name):
    '''/rnr/works'''
    return render_to_response(template_name)

@request_type('GET', False)
@lang_aware(rnr_notifications_telmpates)
def rnr_notifications(request, template_name):
    '''/rnr/notifications'''
    return render_to_response(template_name)

@request_type('GET', False)
@lang_aware(rnr_clients_telmpates)
def rnr_clients(request, template_name):
    '''/rnr/clients'''
    return render_to_response(template_name)

@request_type('GET', False)
@lang_aware(rnr_dictionary_templates)
def rnr_dictionary(request, template_name):
    '''/rnr/dict'''
    return render_to_response(template_name)

@request_type('GET', False)
@lang_aware(rnr_about_templates)
def rnr_about(request, template_name):
    '''/rnr/about'''
    return render_to_response(template_name)

