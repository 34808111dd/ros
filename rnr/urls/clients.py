'''
Created on Dec 21, 2014

@author: Coeurl
'''

from django.conf.urls import patterns, url

client_urls = patterns('',
                             url(r'clients_all', 'rnr.views.clients.clients_get_all_json'),
                             url(r'del_contact', 'rnr.views.clients.del_contact'),
                             url(r'get_client_names_json', 'rnr.views.clients.get_client_names_json'),
                             url(r'add_new_client', 'rnr.views.clients.add_new_client'),
                             url(r'del_client', 'rnr.views.clients.del_client'),
                             url(r'get_client_info','rnr.views.clients.get_client_info'),
                             url(r'update_client_info','rnr.views.clients.update_client_info'),
                             )