from django.contrib import admin
from rnr.models import DictRecord, Language, Client, Contact, WorkType, Work, WorkState, NotificationState,\
Notification, NotificationTemplate, NotificationType, OutageTemplate, Outage, OutageType, MaintenanceWindow,\
Location, Region, WorkTypeDescription, WorkLocationDescription, WorkRegionDescription,\
NotificationTypeDescription, OutageTypeDescription, NotificationStateDescription, OutageConditions,\
AppErrorType, AppErrorDescription

admin.site.register(DictRecord)
admin.site.register(Language)
admin.site.register(Client)
admin.site.register(Contact)
admin.site.register(MaintenanceWindow)
admin.site.register(Location)
admin.site.register(Region)


admin.site.register(Work)
admin.site.register(WorkState)
admin.site.register(WorkType)
admin.site.register(WorkTypeDescription)
admin.site.register(WorkLocationDescription)
admin.site.register(WorkRegionDescription)


admin.site.register(Notification)
admin.site.register(NotificationType)
admin.site.register(NotificationState)
admin.site.register(NotificationTemplate)
admin.site.register(NotificationTypeDescription)
admin.site.register(NotificationStateDescription)


admin.site.register(Outage)
admin.site.register(OutageTemplate)
admin.site.register(OutageType)
admin.site.register(OutageTypeDescription)
admin.site.register(OutageConditions)


admin.site.register(AppErrorType)
admin.site.register(AppErrorDescription)