'''
Created on Dec 19, 2014

@author: Coeurl
'''

from django.conf.urls import patterns, url

work_urls = patterns('',
                     
                     url(r'load_works', 'rnr.views.works.load_works'),
                     
                     url(r'get_works_json', 'rnr.views.works.get_works_json'),
                     url(r'get_worktypes_all_json', 'rnr.views.works.get_worktypes_all_json'),
                     #?
                     #url(r'get_work_types_json', 'rnr.views.works.get_work_types_json'),
                     url(r'get_work_slug', 'rnr.views.works.get_work_slug'),
                     url(r'get_work_name_json', 'rnr.views.works.get_work_name_json'),
                     url(r'get_work_numbers_json', 'rnr.views.works.get_work_numbers_json'),
                     url(r'get_works_total_count', 'rnr.views.works.get_works_total_count'),
                     
                     url(r'add_new_work', 'rnr.views.works.add_new_work'),
                     
                     url(r'delete_work', 'rnr.views.works.delete_work'),
)
