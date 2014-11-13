from django.db import models
from random import choice
import string
from django.core.exceptions import ValidationError

SLUG_STRING = string.hexdigits
SLUG_LEN = 12

def generate_slug():
    '''
    Slug generation function.
    '''
    return ''.join([choice(SLUG_STRING) for _x in range(0, SLUG_LEN)])

class DictRecord(models.Model):
    '''
    Dictionary record for csv processor
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    init_word = models.CharField(max_length=128)
    replace_word = models.CharField(max_length=128)
    def __unicode__(self):
        return self.init_word + "=>" + self.replace_word
    class Meta(object):
        verbose_name = u'Dictionary record'
        verbose_name_plural = u'Dictionary records'

class Language(models.Model):
    '''
    Language for notification
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    language_name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.language_name
    class Meta(object):
        verbose_name = u'Language'
        verbose_name_plural = u'Languages'

class Client(models.Model):
    '''
    Client
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    client_name = models.CharField(unique=True, max_length=128)
    client_language = models.ForeignKey('Language')
    def __unicode__(self):
        return self.client_name
    class Meta(object):
        verbose_name = u'Client'
        verbose_name_plural = u'Clients'

class Contact(models.Model):
    '''
Contacts
    '''
#---added false to unique
    slug = models.SlugField(unique=True, default=generate_slug)
    client = models.ForeignKey('Client')
    contact_email = models.EmailField(unique=False)
    
    def delete(self, *args, **kargs):
        if Contact.objects.filter(client=self.client).count() > 1:
            super(Contact, self).delete(*args, **kargs)
        else:
            raise ValidationError("no way!")
        print Contact.objects.filter(client=self.client).count()
    
    def __unicode__(self):
        return self.contact_email
    class Meta(object):
        verbose_name = u'Contact'
        verbose_name_plural = u'Contacts'

class WorkType(models.Model):
    '''
    Type of work
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    worktype_name = models.CharField(max_length=128)
    def __unicode__(self):
        return self.worktype_name

class WorkState(models.Model):
    '''
    State of works:
    Completed (blue), Pending(yellow), Upcoming(green/red), Canceled(white)
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    workstate_name = models.CharField(unique=True, max_length=128)
    def __unicode__(self):
        return self.workstate_name

class Work(models.Model):
    '''
    Works on network
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    work_number = models.CharField(unique=True, max_length=128)
    work_type = models.ForeignKey('WorkType')
    work_circuit = models.CharField(max_length=128)
    work_start_date = models.DateTimeField()
    work_end_date = models.DateTimeField()
#    work_location = models.ForeignKey('Location')
    work_region = models.ForeignKey('Region')
    work_state = models.ForeignKey('WorkState', null=True, blank=True)
    work_added = models.DateTimeField()
    
    def save(self, *args, **kargs):
        self.work_state = WorkState.objects.get(id=1)
        
        
        super(Work, self).save(*args, **kargs)
    
    def __unicode__(self):
        return self.work_number
    class Meta(object):
        verbose_name = u'Work'
        verbose_name_plural = u'Works'
        
        

class OutageConditions(models.Model):
    '''
    Model for outage conditions:
    2-8 ZAK, 2-8 KRP, 4-6 etc
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    outagecond_name = models.CharField(max_length=64)
    outagecond_description = models.CharField(max_length=128)
    outagecond_translation = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.outagecond_name


class OutageType(models.Model):
    '''
    Type for outage (degradation, backup, full close)
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    outagetype_name = models.CharField(max_length=128)
#    outagetype_description = models.ForeignKey('OutageDefinition')
    def __unicode__(self):
        return self.outagetype_name

class Outage(models.Model):
    '''
    Every Notification has fiew outages with different outage types
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    outage_type = models.ForeignKey('OutageType')
    outage_mw = models.ForeignKey('MaintenanceWindow')
    outage_circuit = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.outage_mw.mw_notification.notification_client.client_name + " " +\
            self.outage_circuit + " " +\
            self.outage_type.outagetype_name + " " +\
            self.outage_mw.mw_start_date.ctime() + "-" +\
            self.outage_mw.mw_end_date.ctime()

class NotificationState(models.Model):
    '''
    Notification state
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    notificationstate_name = models.CharField(max_length=128)
    notificationstate_description = models.CharField(max_length=128)
    def __unicode__(self):
        return self.notificationstate_name

def get_default_state():
    '''
    for initial state of notification
    '''
    return NotificationState.objects.get(id=1)

class Notification(models.Model):
    '''
    Notification
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    notification_send_date = models.DateTimeField(null=True, blank = True)
    notification_state = models.ForeignKey('NotificationState',\
                                           default=get_default_state)
    notification_work = models.ForeignKey('Work')
    notification_client = models.ForeignKey('Client')
    notification_type = models.ForeignKey('NotificationType')
    notification_subject = models.TextField()
    notification_complete_text = models.TextField()
    
    def __unicode__(self):
        return self.notification_client.client_name +\
            " " + self.notification_state.notificationstate_name +\
            " " + self.notification_work.work_number

class NotificationTemplate(models.Model):
    '''
    Notification Template - information, 
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    notificationtemplate_name = models.CharField(max_length=128)
    notificationtemplate_language = models.ForeignKey('Language')
    notification_type = models.ForeignKey('NotificationType')
    notificationtemplate_subject = models.CharField(max_length=128)
    notificationtemplate_text = models.TextField()
    
    def __unicode__(self):
        return self.notificationtemplate_name

class NotificationType(models.Model):
    '''
    Notification Template - information, canceling, time_change(?)
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    notificationtype_name = models.CharField(max_length=128)
    def __unicode__(self):
        return self.notificationtype_name
    
class OutageTemplate(models.Model):
    '''
    outage template - language(), outage type
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    outagetemplate_name = models.CharField(max_length=128)
    outagetemplate_language = models.ForeignKey('Language')
    outagetemplate_outagetype = models.ForeignKey('OutageType')
    outagetemplate_text = models.TextField()
    def __unicode__(self):
        return self.outagetemplate_name
    
class Location(models.Model):
    '''
    Location of work
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    location_name = models.CharField(max_length=128)
    def __unicode__(self):
        return self.location_name
    
class Region(models.Model):
    '''
    Region of work
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    region_location = models.ForeignKey('Location')
    region_name = models.CharField(max_length=128)
    def __unicode__(self):
        return self.region_name
    
class MaintenanceWindow(models.Model):
    '''
    Every Notification is based on average MW, every MW has one or several Outages. 
    '''
    slug = models.SlugField(unique=True, default=generate_slug)
    mw_notification = models.ForeignKey('Notification')
    mw_start_date = models.DateTimeField()
    mw_end_date = models.DateTimeField()
    
    def __unicode__(self):
        return self.mw_notification.notification_work.work_number + " " +  \
            self.mw_notification.notification_client.client_name + " " + \
            self.mw_start_date.strftime('%d.%m.%Y %H:%M') + "-" + \
            self.mw_end_date.strftime('%d.%m.%Y %H:%M')
            
            
#===============================================================================
# Localization objects
#===============================================================================

class WorkTypeDescription(models.Model):
    slug = models.SlugField(unique=True, default=generate_slug)
    worktypelang = models.ForeignKey('Language')
    worktype = models.ForeignKey('WorkType')
    worktypedesc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.worktypelang.language_name + " " + self.worktype.worktype_name
    
class WorkLocationDescription(models.Model):
    slug = models.SlugField(unique=True, default=generate_slug)
    worklocationlang = models.ForeignKey('Language')
    worklocation = models.ForeignKey('Location')
    worklocdesc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.worklocationlang.language_name + " " + self.worklocation.location_name
    
    
class WorkRegionDescription(models.Model):
    slug = models.SlugField(unique=True, default=generate_slug)
    workregionlang = models.ForeignKey('Language')
    workregion = models.ForeignKey('Region')
    workregdesc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.workregionlang.language_name + " " + self.workregion.region_name
    
class NotificationTypeDescription(models.Model):
    slug = models.SlugField(unique=True, default=generate_slug)
    notificationtypelang = models.ForeignKey('Language')
    notificationtype = models.ForeignKey('NotificationType')
    notificationtypedesc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.notificationtypelang.language_name + " " + self.notificationtype.notificationtype_name
    
    
class OutageTypeDescription(models.Model):
    slug = models.SlugField(unique=True, default=generate_slug)
    outagetypelang = models.ForeignKey('Language')
    outagetype = models.ForeignKey('OutageType')
    outagetypedesc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.outagetypelang.language_name + " " + self.outagetype.outagetype_name
    
class NotificationStateDescription(models.Model):
    slug = models.SlugField(unique=True, default=generate_slug)
    notificationstatelang = models.ForeignKey('Language')
    notificationstate = models.ForeignKey('NotificationState')
    outagetypedesc = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.notificationstatelang.language_name + " " + self.notificationstate.notificationstate_name
    
