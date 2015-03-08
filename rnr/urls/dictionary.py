'''
Created on Jan 8, 2015

@author: Coeurl
'''

from django.conf.urls import patterns, url

dictionary_urls = patterns('',
                              url(r'add_dict_record', 'rnr.views.dictionary.add_dict_record'),
                              url(r'del_dict_record', 'rnr.views.dictionary.del_dict_record'),
                              url(r'get_dict_records', 'rnr.views.dictionary.get_dict_records'),
                              )