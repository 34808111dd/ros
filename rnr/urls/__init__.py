'''
Separate urls must be added to urlpatterns list
'''


from rnr.urls.general import general_urls
from rnr.urls.utility import utility_urls
from rnr.urls.old import old_urls
from rnr.urls.works import work_urls
from rnr.urls.notifications import notification_urls
from rnr.urls.clients import client_urls

from rnr.urls_old import urlpatterns


urlpatterns += general_urls
urlpatterns += utility_urls
urlpatterns += old_urls
urlpatterns += work_urls
urlpatterns += notification_urls
urlpatterns += client_urls
