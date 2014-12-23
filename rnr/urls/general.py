'''
Created on Dec 19, 2014

@author: Coeurl
'''

from django.conf.urls import patterns, url

general_urls = patterns('',
    url(r'^$', 'rnr.views.general.rnr_home'),
    url(r'works/', 'rnr.views.general.rnr_works'),
    url(r'notifications/', 'rnr.views.general.rnr_notifications'),
    url(r'clients/', 'rnr.views.general.rnr_clients'),
    url(r'dictionary/', 'rnr.views.general.rnr_dictionary'),
    url(r'about/', 'rnr.views.general.rnr_about'),
    )
