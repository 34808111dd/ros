from django.conf.urls import patterns, url


urlpatterns = patterns('',
    #Work views
    
    
    
    
    
    
    url(r'get_outage_type_all_json', 'rnr.views_old.get_outage_type_all_json'),
    
    #view_notification
    
    
    url(r'languages_all', 'rnr.views_old.get_languages_all_json'),
    
    url(r'get_locations_all_json', 'rnr.views_old.get_locations_all_json'),
    
#    url(r'clients/', 'rnr.views_old.clients'),
    

    
    
    url(r'get_outages_json', 'rnr.views_old.get_outages_json'),
    

    #url(r'gen_cancel', 'rnr.views_old.gen_cancel'),
    url(r'get_regions_json', 'rnr.views_old.get_regions_json'),
    
    

    
    
    
    url(r'get_message_queue_len', 'rnr.views_old.get_message_queue_len'),
    url(r'reset_message_queue', 'rnr.views_old.reset_message_queue'),
    
    url(r'data', 'rnr.views_old.data'),
    url(r'tmp_req', 'rnr.views_old.tmp_req'),
)
