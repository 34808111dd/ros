'''
Created on Dec 19, 2014

@author: Coeurl
'''

from django.conf.urls import patterns, url

utility_urls = patterns('',
    url(r'set_language/','rnr.views.utility.set_language'),
    )
