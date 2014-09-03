from django.contrib import admin
#from fns_django.mail_manager.models import Messages, Attachments, Headers, Threads
from rnr.models import DictRecord, Language, Client, Contact, WorkType, Work, NotificationState, Notification, Template, Outage

admin.site.register( DictRecord )
admin.site.register( Language )
admin.site.register( Client )
admin.site.register( Contact )
admin.site.register( WorkType )
admin.site.register( Work )
admin.site.register( NotificationState )
admin.site.register( Notification )
admin.site.register( Template )
admin.site.register( Outage )
