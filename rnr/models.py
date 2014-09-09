from django.db import models

# Create your models here.


from random import choice
import string

SLUG_STRING = string.hexdigits
SLUG_LEN = 12

def GenerateSlug():
    '''
    GEN SLUG
    '''
    return ''.join([ choice( SLUG_STRING ) for _x in range( 0, SLUG_LEN )])

   
class DictRecord(models.Model):
    '''
    Dictionary record
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    init_word = models.CharField( max_length=128 )
    replace_word = models.CharField ( max_length=128 )
    
    def __unicode__(self):
        return self.init_word + "=>" + self.replace_word
    
    class Meta(object):
        verbose_name = u'Dictionary record'
        verbose_name_plural = u'Dictionary records'


class Language(models.Model):
    '''
    Language for notification
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    language_name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.language_name

    class Meta(object):
        verbose_name = u'Notification Language'
        verbose_name_plural = u'Notification Languages'

class Client(models.Model):
    '''
    Client
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
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
    slug = models.SlugField( unique=True, default=GenerateSlug )
    client = models.ForeignKey('Client')
    contact_email = models.EmailField(unique = True)
    
    def __unicode__(self):
        return self.contact_email
    
    class Meta(object):
        verbose_name = u'Contact'
        verbose_name_plural = u'Contacts'



class WorkType(models.Model):
    '''
    Type of work
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    worktype_name = models.CharField(max_length =128)
    
    def __unicode__(self):
        return self.worktype_name

class Work(models.Model):
    '''
    Works on network 
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    work_number = models.CharField(unique = True, max_length = 128)
    work_type = models.ForeignKey('WorkType')
    work_circuit = models.CharField(max_length = 128)
    work_start_date = models.DateTimeField()
    work_end_date = models.DateTimeField()
    work_definition = models.CharField(max_length =128)
    
    def __unicode__(self):
        return self.work_number
    
    class Meta(object):
        verbose_name = u'Work on net'
        verbose_name_plural = u'Works on net'
        
        
class Outage(models.Model):
    '''
    Outage type
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    outage_name = models.CharField(max_length = 128)
    outage_description = models.TextField()
    
    def __unicode__(self):
        return self.outage_name

class NotificationState(models.Model):
    '''
    Notification state
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    notification_state = models.CharField(max_length = 128)
    notification_state_description = models.TextField()
    
    def __unicode__(self):
        return self.notification_state

def get_default_state():
    return NotificationState.objects.get(id=1)
 

class Notification(models.Model):
    '''
    Notification
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    notification_send_date = models.DateTimeField(null=True, blank = True)
    notification_state = models.ForeignKey('NotificationState', default=get_default_state)
    notification_work = models.ForeignKey('Work')
    notification_client = models.ForeignKey('Client')
    notification_outage = models.ForeignKey('Outage')
    notification_template = models.ForeignKey('Template')
    
        
    def __unicode__(self):
        return self.notification_client.client_name + " " + self.notification_outage.outage_name + " " + self.notification_state.notification_state + " " + self.notification_work.work_number
    
class Template(models.Model):
    '''
    Template
    '''
    slug = models.SlugField( unique=True, default=GenerateSlug )
    template_name = models.CharField(max_length = 128)
    template_language = models.ForeignKey('Language')
    template_client = models.ForeignKey('Client', null=True, blank=True)
    template_worktype = models.ForeignKey('WorkType')
    template_outage = models.ForeignKey('Outage')
    template_text = models.TextField()
    
    def __unicode__(self):
        return self.template_name