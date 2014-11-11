from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#import views


#===============================================================================
# /clients (/add /del /edit)
# /contacts 
# /notifications
# /works
# /
#===============================================================================

urlpatterns = patterns('',
    url(r'^$', 'rnr.views.rnr_home'),
    url(r'works/', 'rnr.views.rnr_works'),
    url(r'clients/', 'rnr.views.rnr_clients'),
    url(r'notifications/', 'rnr.views.rnr_notifications'),
    
    url(r'clients_all', 'rnr.views.clients_get_all_json'),
    url(r'del_contact', 'rnr.views.del_contact'),
    url(r'get_work_name_json', 'rnr.views.get_work_name_json'),
    url(r'get_client_names_json', 'rnr.views.get_client_names_json'),
    url(r'save_notification', 'rnr.views.save_notification'),
    url(r'get_outage_type_all_json', 'rnr.views.get_outage_type_all_json'),
    url(r'send_notification', 'rnr.views.send_notification'),
    url(r'send_all_notifications', 'rnr.views.send_all_notifications'),
    url(r'view_notification', 'rnr.views.view_notification'),
    url(r'delete_work', 'rnr.views.delete_work'),
    url(r'update_notification', 'rnr.views.update_notification'),
    url(r'del_notification', 'rnr.views.del_notification'),
    
    #view_notification
    url(r'load_works', 'rnr.views.load_works'),
    url(r'get_notification_type_all_json', 'rnr.views.get_notification_type_all_json'),
    
    url(r'languages_all', 'rnr.views.get_languages_all_json'),
    url(r'get_worktypes_all_json', 'rnr.views.get_worktypes_all_json'),
       url(r'get_locations_all_json', 'rnr.views.get_locations_all_json'),
    
    url(r'csv_parser/', 'rnr.views.csv_parser'),
    url(r'csv_process/', 'rnr.views.csv_process'),
    url(r'add_new_record/', 'rnr.views.add_new_record'),
    url(r'del_record/','rnr.views.delete_record'),
#    url(r'clients/', 'rnr.views.clients'),
    url(r'set_language/','rnr.views.set_language'),
    url(r'add_new_client', 'rnr.views.add_new_client'),
    url(r'del_client', 'rnr.views.del_client'),
    url(r'get_work_types_json', 'rnr.views.get_work_types_json'),
    url(r'get_works_json', 'rnr.views.get_works_json'),
    url(r'get_notifications_json', 'rnr.views.get_notifications_json'),
    url(r'get_outages_json', 'rnr.views.get_outages_json'),
    url(r'add_new_work', 'rnr.views.add_new_work'),
    url(r'add_new_notification', 'rnr.views.add_new_notification'),
    url(r'gen_notification', 'rnr.views.gen_notification'),
    url(r'gen_cancel', 'rnr.views.gen_cancel'),
    url(r'get_regions_json', 'rnr.views.get_regions_json'),
    url(r'test_bootstrap', 'rnr.views.test_bootstrap'),
    url(r'about', 'rnr.views.rnr_about'),
    
#    url(r'^([0-9]+)/$','video.views.sub_sections'),
#    url(r'^([0-9]+)/([0-9]+)$','video.views.videos'),
    # Examples:
    # url(r'^$', 'rostelecom.views.home', name='home'),
    # url(r'^rostelecom/', include('rostelecom.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
