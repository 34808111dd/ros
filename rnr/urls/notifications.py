'''
Created on Dec 19, 2014

@author: Coeurl
'''


from django.conf.urls import patterns, url

notification_urls = patterns('',
                              url(r'save_notification', 'rnr.views.notifications.save_notification'),
                              url(r'send_notification', 'rnr.views.notifications.send_notification'),
                              url(r'send_all_notifications', 'rnr.views.notifications.send_all_notifications'),
                              url(r'view_notification', 'rnr.views.notifications.view_notification'),
                              url(r'update_notification', 'rnr.views.notifications.update_notification'),
                              url(r'del_notification', 'rnr.views.notifications.del_notification'),
                              url(r'get_notification_type_all_json', 'rnr.views.notifications.get_notification_type_all_json'),
                              url(r'get_notifications_json', 'rnr.views.notifications.get_notifications_json'),
                              url(r'add_new_notification', 'rnr.views.notifications.add_new_notification'),
                              url(r'gen_notification', 'rnr.views.notifications.gen_notification'),
                              )