'''
Created on Dec 19, 2014

@author: Coeurl
'''

from django.conf.urls import patterns, url

old_urls = patterns('',
    url(r'csv_parser/', 'rnr.views.old.csv_parser'),
    url(r'csv_process/', 'rnr.views.old.csv_process'),
    url(r'add_new_record/', 'rnr.views.old.add_new_record'),
    url(r'del_record/','rnr.views.old.delete_record'),
    )