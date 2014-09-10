from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#import views

urlpatterns = patterns('',
    url(r'^$', 'rnr.views.rnr_home'),
    url(r'csv_parser/', 'rnr.views.csv_parser'),
    url(r'csv_process/', 'rnr.views.csv_process'),
    url(r'add_new_record/', 'rnr.views.add_new_record'),
    url(r'del_record/','rnr.views.delete_record'),
    url(r'clients/', 'rnr.views.clients'),
    url(r'clients_all', 'rnr.views.clients_get_all_json'),
    url(r'add_new_client', 'rnr.views.add_new_client'),
    url(r'get_work_types_json', 'rnr.views.get_work_types_json'),
    url(r'add_new_work', 'rnr.views.add_new_work'),
    
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
