'''
Created on Oct 16, 2014

@author: Coeurl
'''

from rnr.models import Work, Client, WorkType, Region, WorkState, Notification, NotificationType, MaintenanceWindow, Outage,\
 OutageType, NotificationTemplate, OutageTemplate, WorkLocationDescription, WorkRegionDescription, DictRecord, Language, OutageConditions
import csv
from django.utils import timezone
#from datetime import datetime
from collections import namedtuple
from processor.errors import FileParseError, TimeParseError, UnknownWorkConditionError, UnknownClient, BlankWorkNumber


#from processor.errors import RecordParseError

FileRecord = namedtuple("FileRecord", ['client', 'date','condition','work_number', 'trakt', 'point', 'description', 'direction', 'type_of_use'])
WorkRecord = namedtuple("WorkRecord",['work_number','work_types'])
ClientRecord = namedtuple("ClientRecord", ['client', 'start_date','end_date' ,'condition','work_number', 'trakt', 'point', 'description', 'direction', 'type_of_use'])

Format1TimeString = namedtuple("Format1TimeString", ['start_week_day', 'start_date', 'from_', 'start_time', 'to_', 'end_time'])
Format2TimeString = namedtuple("Format2TimeString", ['from_', 'start_time', 'start_week_day','start_date', 'to_', 'end_time','end_week_day', 'end_date'])

Date = namedtuple("Date",['day','month','year'])
Time = namedtuple("Time",['hour','minute'])

local_tz = timezone.get_current_timezone()
utc_tz = timezone.utc


class LocalWork():
    def __init__(self, work_number, work_type, work_start_date, work_end_date, work_region, work_state):
        self.work_number = work_number
        self.work_type = work_type
        self.work_start_date = work_start_date
        self.work_end_date = work_end_date
        self.work_region = work_region
        self.work_state = work_state
        self.notifications = []
    
    
    def save(self, save_date, merge_notifications = False):
        '''
        TODO - remove UGLY code
        '''
        
        
        if merge_notifications == False:
            
            tmp_work_obj=Work(work_number=self.work_number,work_type=self.work_type,\
                              work_start_date=self.work_start_date,\
                              work_end_date=self.work_end_date, work_region=self.work_region,\
                              work_state=self.work_state, work_added=save_date)
            tmp_work_obj.save()
            
            
            for notification in self.notifications:
            
            
                notif_dj_obj = Notification(notification_work=tmp_work_obj, notification_client=notification.client,\
                                            notification_type=notification.notification_type,\
                                            notification_subject = notification.notification_subject,\
                                            notification_complete_text = notification.notification_complete_text)
                notif_dj_obj.save()
                
                for mw in notification.mws:
                    mw_django_obj = MaintenanceWindow(mw_notification=notif_dj_obj,\
                                                      mw_start_date=mw.mw_start_date,\
                                                      mw_end_date=mw.mw_end_date)
                    mw_django_obj.save()
                    
                    for outage in mw.outages:
                        outage_django_obj = Outage(outage_type=outage.outage_type,\
                                                   outage_mw=mw_django_obj, outage_circuit=outage.outage_circuit)
                        outage_django_obj.save()
            
            
        else:
            tmp_work_obj = Work.objects.get(work_number=self.work_number)
            
            work_notification_client_objs = [ _x[0] for _x in Notification.objects.filter(notification_work=tmp_work_obj).values_list('notification_client__client_name')]
            
            for notification in self.notifications:
                
                if notification.client.client_name not in work_notification_client_objs:
                    notif_dj_obj = Notification(notification_work=tmp_work_obj, notification_client=notification.client,\
                                                notification_type=notification.notification_type,\
                                                notification_subject = notification.notification_subject,\
                                                notification_complete_text = notification.notification_complete_text)
                    notif_dj_obj.save()
                    
                    for mw in notification.mws:
                        mw_django_obj = MaintenanceWindow(mw_notification=notif_dj_obj,\
                                                      mw_start_date=mw.mw_start_date,\
                                                      mw_end_date=mw.mw_end_date)
                        mw_django_obj.save()
                    
                    for outage in mw.outages:
                        outage_django_obj = Outage(outage_type=outage.outage_type,\
                                                   outage_mw=mw_django_obj, outage_circuit=outage.outage_circuit)
                        outage_django_obj.save()
            
#===============================================================================
#             for notification in self.notifications:
# 
# 
#                   notif_dj_obj = Notification(notification_work=tmp_work_obj, notification_client=notification.client,\
#                                               notification_type=notification.notification_type,\
#                                               notification_subject = notification.notification_subject,\
#                                               notification_complete_text = notification.notification_complete_text)
#                 notif_dj_obj.save()
# 
#                 for mw in notification.mws:
#                       mw_django_obj = MaintenanceWindow(mw_notification=notif_dj_obj,\
#                                                         mw_start_date=mw.mw_start_date,\
#                                                         mw_end_date=mw.mw_end_date)
#                     mw_django_obj.save()
# 
#                     for outage in mw.outages:
#                           outage_django_obj = Outage(outage_type=outage.outage_type,\
#                                                      outage_mw=mw_django_obj, outage_circuit=outage.outage_circuit)
#                         outage_django_obj.save()
#===============================================================================
                
        
    def __str__(self):
        return str(len(self.notifications))

class LocalNotification():
    def __init__(self, client, notification_type):
        self.client = client
        self.notification_type = notification_type
        self.notification_subject = ""
        self.notification_complete_text = ""
        self.mws = []
        

class Local_MW():
    def __init__(self, mw_start_date, mw_end_date):
        self.mw_start_date = mw_start_date
        self.mw_end_date = mw_end_date
        self.outages = []
        
class LocalOutage():
    def __init__(self, outage_type, outage_circuit):
        self.outage_type = outage_type
        self.outage_circuit = outage_circuit
        
class WorkContainer(object):
    '''
    Class for parsing csv and saving new objects in db
    
    Caching:
    WorkType
    Region
    WorkState
    Clients
    NotificationTypes
    OutageType
    NotificationTemplate
    MaintenanceWindow
    '''


    def __init__(self, file_descriptor):
        '''
        Work Container
        input from request
        '''
        
        
        self.WorkTypes = []
        self.Regions = []
        self.WorkStates = []
        self.Clients = []
        self.NotificationTypes = []
        self.OutageTypes = []
        self.OutageTemplates = []
        self.NotificationTemplates = []
        self.Works = []
        self.Languages = []
        self.translate_dictionary = {}
        self.EngLanguage = None
        self.OutageConditions = []
        
        self.WorkRegionDescriptions = []
        self.WorkLocationDescriptions = []
    
        #populate cache
#        print datetime.now()
        self.populate_cache()
#        print datetime.now()
        
        reader = csv.reader(file_descriptor, delimiter=';', quotechar='"')
        #skip first lines
        try:
            for _line_tuple in reader:
                if len(_line_tuple[0]) == 1:
                    break
    #Raise file parsing error on wrong file format or encoding
            #self.contents = [ FileRecord(*_x) for _x in reader]
            self.contents = [ FileRecord(*[y.decode('1251') for y in _x]) for _x in reader]
            if len(self.contents)==0:
                raise Exception
        except Exception:
            raise FileParseError("")
        finally:
            file_descriptor.close()
        
        
    def populate_cache(self):
        '''
        Load variables from database
        '''
        self.WorkTypes = WorkType.objects.all()
        self.Regions = Region.objects.all()
        self.WorkStates = WorkState.objects.all()
        self.Clients = Client.objects.all()
        self.NotificationTypes = NotificationType.objects.all()
        self.OutageTypes = OutageType.objects.all()
        self.NotificationTemplates = NotificationTemplate.objects.all()
        self.OutageTemplates = OutageTemplate.objects.all()
        self.Languages = Language.objects.all()
        
        self.WorkRegionDescriptions = WorkRegionDescription.objects.all()
        self.WorkLocationDescriptions = WorkLocationDescription.objects.all()
        self.OutageConditions = OutageConditions.objects.all()
        
        #self.EngLanguage = filter(lambda _x: _x.language_name == "English", self.Languages)[0]
        self.EngLanguage = Language.objects.get(language_name="English") #filter(lambda _x: _x.language_name == "English", self.Languages)[0]
        
        for _x in DictRecord.objects.all():
            self.translate_dictionary[_x.init_word] = _x.replace_word
#        print len(self.translate_dictionary)
#        print self.translate_dictionary

    def save_cached(self, same_work_options):
        '''
        Save work, Notifications, MW, outages
        '''
        
        #print same_work_options
        
        work_numbers = [ _x[0] for _x in Work.objects.values_list('work_number')]
        #print work_numbers
        
        if same_work_options == 'ReplaceOld':
            pass
        if same_work_options == 'MergeNotifications':
            pass
        if same_work_options == 'IgnoreNew':
            pass
        
        
        add_date = timezone.now()
        
        for loc_work in self.Works:
            
            if loc_work.work_number in work_numbers:
                print "Existing work found."
            
                if same_work_options == 'ReplaceOld':
                    django_db_work_obj = Work.objects.get(work_number = loc_work.work_number)
                    django_db_work_obj.delete()
                    loc_work.save(add_date)
                if same_work_options == 'IgnoreNew':
                    pass
                if same_work_options == 'MergeNotifications':
                    loc_work.save(add_date, merge_notifications=True)
                
            else:
                loc_work.save(add_date)
            
            
        
#        print self.Works
        
        #[_x.save() for _x in cls.Works.keys()]
        #pass
        #
        
#        for _x in cls.Works:
#            print "saving work",_x.work_number
#            _x.save()
#            print "saved work_id", _x.id
        
        #[_x.save() for _x in cls.Notifications]
        #print cls.Notifications
        #for _x in cls.Notifications:
        #    
        #    
        #    print _x.notification_send_date
        #    print _x.notification_state
        #    print _x.notification_work.id
        #    print _x.notification_client
        #    print _x.notification_type
        #    print _x.notification_subject
        #    print _x.notification_complete_text
            
            
        #    print "saving notification", _x.notification_work.id
        #    _x.save()
        
        
        #[_x.save() for _x in cls.MaintenanceWindows]
        #[_x.save() for _x in cls.Outages]
        
        
        
    def lookup_region(self, work_number):
        '''
        returns region and location
        '''
        
        region_code = work_number.split("/")[0]
        t_d = {'03':'Northwestern region',
'05':'Volga region',
'14':'Ural region',
'15':'Far East region',
'09':'South region',
'08':'Siberia region',
'20':'Central region',
'21':'Central region',
'00':'Somewhere'
}
        if region_code in t_d.keys():
            region_django_obg = filter(lambda _x: _x.region_name==t_d[region_code], self.Regions)[0]
        else:
            region_django_obg = filter(lambda _x: _x.region_name==t_d["00"], self.Regions)[0]
            
        return region_django_obg 
    
    def parse(self, file_parse_options, same_work_options):
        '''
        parse contents of file
        '''
        
        work_numbers = set([_x.work_number for _x in self.contents])
#        print work_numbers
        
        if '' in work_numbers:
            raise BlankWorkNumber("")
        
        #cycle works
        for work_number in work_numbers:
            #filter current work records, TODO - rework to reduce cycle count
            work_records = filter(lambda x: x.work_number == work_number, self.contents)
#Search WorkType object in cache
            worktype_dj_obj = filter(lambda _x: _x.id==2, self.WorkTypes)[0]

#TODO Replace it with work info

            #work_circuit = ', '.join(list(set([x.point for x in work_records]))[:3])
            #select max and min work dates
            work_dates = set([x.date for x in work_records])
            
            try:
                
            #If error, raise TimeParseError, then raise RecordParseError
                work_start_date, work_end_date = self.find_work_start_end_dates(work_dates)
            except Exception:
                raise TimeParseError(work_number)
#            print work_start_date, work_end_date
#TODO get value from cache, not from DB
            work_region_dj_obj = self.lookup_region(work_number)
            #work_region_dj_obj = filter(lambda _x: _x.id==3, self.Regions)[0]
#TODO get valuse from cache
            work_state_dj_obj = filter(lambda _x: _x.id==1, self.WorkStates)[0]
#Create work
            #local_work_obj = Work(work_number=work_number, work_type=work_type,\
            #                    work_circuit=work_circuit, work_start_date=work_start_date,\
            #                    work_end_date=work_end_date, work_region=work_region,\
            #                    work_state=work_state)
            #local_work_obj.save()
            local_work_obj = LocalWork(work_number=work_number, work_type=worktype_dj_obj,\
                                     work_start_date=work_start_date,\
                                     work_end_date=work_end_date, work_region=work_region_dj_obj,\
                                     work_state=work_state_dj_obj)
            
#            print type(local_work_obj), local_work_obj
            self.Works.append(local_work_obj)
            
#            print 'work appended', len(self.Works)
            if file_parse_options != 'CreateWorksOnly':
#                self.save_cached(same_work_options)
#                return None
#Get Clients affected
                work_clients = set([x.client.split(';')[0].strip() for x in work_records])
                for client_name in work_clients:
                    client_file_records = filter(lambda x:x.client.split(';')[0].strip()==client_name, work_records)
                    self.create_notifications(client_file_records, client_name, local_work_obj)
                    
        if file_parse_options != 'CheckErrors':
            self.save_cached(same_work_options)
                
#            print len(self.Works)
#        if 
#        self.save_cached(same_work_options)
            
            #work_records = filter(lambda x: x.work_number == work_number, self.contents)
            #work_date = set(_record.date for _record in work_records)
            #work_clients = set(_record.client for _record in work_records)
            #print '----'
            #print work_number, work_date
            #for client_name in work_clients:
            #    work_channels = set([channel.direction.split(' ')[-1] for channel in filter(lambda x: x.client == client_name, work_records)])
            #    print client_name
            #    print len(work_channels)
   
    def translate_client_channel_name(self, channel_string):
        
        #cell_contents = cell_contents.decode(self.parse_options.options['output_encoding'])
        
        for k,v in self.translate_dictionary.items():
            f_index = channel_string.lower().find(k.lower())
            while f_index != -1:
                channel_string = channel_string[:f_index] + v + channel_string[f_index+len(k):]
                f_index = channel_string.lower().find(k.lower())
        return channel_string #.encode(self.parse_options.options['output_encoding'])
        
    def lookup_outage_type(self, outages_set):
        
#TODO error on looking up translation for non-existing OutageCondition (4-6 KR == 4-6 KRP)
        
        '''
        return outage type object
        '''
#        print "looking up outages:"

        translated = []
        
        #for x in outages_set:
        #    print x
        #print self.OutageConditions
        
        for x in outages_set:
            try:
                outage_translated = filter(lambda _x: _x.outagecond_name == x, self.OutageConditions)[0]
                if outage_translated:
                    translated.append(outage_translated.outagecond_translation)
            except:
                raise UnknownWorkConditionError(x)
                    
        if len(translated) == 1:
            if "2-8 KRP" not in translated and "4-6 KRP" not in translated:
                return filter(lambda _x: _x.outagetype_name == "service_interruption", self.OutageTypes)[0]
            else:
                return filter(lambda _x: _x.outagetype_name == "service_degradation", self.OutageTypes)[0]
        elif len(translated) == 2:
            if "4-6" in translated or "4-6 KRP" in translated:
                return filter(lambda _x: _x.outagetype_name == "service_interruption_50ms", self.OutageTypes)[0]
            
        else:
            return None
        
    def create_notifications(self, work_client_records, client_name, local_work_object):
        '''
        format input records, filter unique MW-s, filter channels based on filtered MWs
        
        '''
#        print "creating notifications for",client_name, local_work_object, type(local_work_object)
#TODO - 

#        print '-> start client search', datetime.now()
        try:
            client_obj = filter(lambda _x: _x.client_name == client_name, self.Clients)[0]
        except IndexError as e:
            raise UnknownClient(client_name)
#        print '<- end client search', datetime.now()
        
        
        
#        print '-> start creating notification object', datetime.now()
        notification_type_obj = filter(lambda _x: _x.id==1, self.NotificationTypes)[0]
        
        
        
        
        #=======================================================================
        # self.notification_send_date = notification_send_date
        # self.notification_state = notification_state
        # self.notification_client = notification_client
        # self.notification_type_obj = notification_type_obj
        # self.notification_subject = notification_subject
        # self.notification_complete_text = notification_complete_text
        #=======================================================================
        
        
        #loc_notif_obj = Notification(notification_work=local_work_object, notification_client= client_obj,\
        #                         notification_type_obj=notification_type_obj, notification_subject="", notification_complete_text="")
        
        loc_notif_obj = LocalNotification(client_obj, notification_type_obj)
        
        local_work_object.notifications.append(loc_notif_obj)
#        print "total notifications", len(local_work_object.notifications)
        #loc_notif_obj.save()
        #convert records's client name to tupical
        client_records = []
        
        #Remove duplicated records with the same MW
        for _x in work_client_records:
            MW_time = self.convert_to_python_datetime(_x.date)
            new_record = FileRecord(client_name, (MW_time[0], MW_time[1]), *_x[2:])
            client_records.append(new_record)
            
        client_record_unique = set(client_records)
        #select unique MWs for client in this work
        MWs = set([_x.date for _x in client_record_unique])
#        _l=datetime.now()
#        print '-> start MW processing', _l
        for MW in MWs:
            #print MW
            #Local_MW_obj = MaintenanceWindow(mw_notification = loc_notif_obj, mw_start_date=MW[0], mw_end_date=MW[1])
            Local_MW_obj = Local_MW(mw_start_date=MW[0], mw_end_date=MW[1])
            loc_notif_obj.mws.append(Local_MW_obj)
            #Local_MW_obj.save()
            #self.MaintenanceWindows.append(Local_MW_obj)
            MW_records = filter(lambda _x: _x.date==MW,  client_record_unique)
            #print 'total records in MW', len(MW_records)
            mw_channels = set([_x.direction for _x in MW_records])
            
            for mw_channel in mw_channels:
                #print mw_channel, [_x.condition for _x in filter(lambda _x: _x.direction==mw_channel,  MW_records)]
                
#TODO - rework to speedup
                MW_records_for_channel = filter(lambda _x: _x.direction==mw_channel,  MW_records)
                mw_channel_outage_codes = set([_x.condition for _x in MW_records_for_channel])
#                print "CURRENT CONDITIONs", mw_channel_outage_codes
                self.lookup_outage_type(mw_channel_outage_codes)
                
                outage_type_dj_obj = self.lookup_outage_type(mw_channel_outage_codes)
                
                #outage_type_dj_obj = filter(lambda _x: _x.id==1, self.OutageTypes)[0]
                #outage_object = Outage(outage_type = outage_type, outage_mw=Local_MW_obj, outage_circuit=mw_channel)
                
#TODO - REPLACE UGLY CODE
                loc_id = mw_channel.split('[')[1].strip()[:-1]
                chan = mw_channel.replace('['+loc_id+']', ' ')
#BUG with disappeared - symbol in channel name.
                #chan = ' '.join([x for x in chan.split(' ') if len(x)>1]) + ' (' + loc_id + ')'
                chan += ' (' + loc_id + ')'
                while chan.find('  ')!=-1:
                    chan=chan.replace('  ', ' ')
                while chan.find(' ;')!=-1:
                    chan=chan.replace(' ;', ';')
                if client_obj.client_language == self.EngLanguage:
                    outage_object = LocalOutage(outage_type = outage_type_dj_obj, outage_circuit=self.translate_client_channel_name(chan))
                else:
                    outage_object = LocalOutage(outage_type = outage_type_dj_obj, outage_circuit=chan)
                
                Local_MW_obj.outages.append(outage_object)
                #outage_object.save()
                #self.Outages.append(outage_object)
#        print '<- end MW Processing',(_l - datetime.now()).microseconds
        
        
#        _l=datetime.now()
#        print '-> start forming body', _l
        loc_notif_obj.notification_subject, loc_notif_obj.notification_complete_text = self.gen_notification_body(loc_notif_obj, local_work_object)
        #loc_notif_obj.notification_subject = ""
        #loc_notif_obj.notification_complete_text = ""
#        print '<- end forming body',(_l - datetime.now()).microseconds
        #loc_notif_obj.save()
        
        
        #transaction.commit()
        #get unique channel's names
        #client_channels = set([_x.direction for _x in client_record_unique])
        #print len(client_channels)
        
        #for client_channel in client_channels:
        #    print client_channel, [_x.condition for _x in filter(lambda _x: _x.direction==client_channel,  client_record_unique)]
        
        
        
        
        
        #for record in work_client_records:
        #    print client_name, record.direction
        
        
    def convert_to_python_datetime(self,time_string):
        '''
        converts time from text format to datetime.
        Assumed, that time_string is a string in 1252 encoding.
        returns tuple of two date-time objects - start and end.
        convert time to utc, based on local timezone (Europe/Moscow)
        '''
        
        time_list = time_string.split(' ')
        
        if len(time_list)==6:
            '''
            No end_date provided, assuming it is equal start_date
            some works have strange time format: Tue 09.12.2014 from 23:00 to 24:00
            '''
            format1time = Format1TimeString(*time_list)
            
            start_date = Date(*[int(_x) for _x in format1time.start_date.split(".")])
            start_time = Time(*[int(_x) for _x in format1time.start_time.split(':')])
            end_time = Time(*[int(_x) for _x in format1time.end_time.split(':')])
            
            #Workaround bug with 24:00 same date
            if end_time.hour == 24 and end_time.minute == 0:
                end_date = timezone.datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute, 0, 0) + timezone.timedelta(days=1)-timezone.timedelta(hours=start_time.hour-1, minutes=60)
                
                return [local_tz.localize(timezone.datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute, 0, 0)).astimezone(timezone.utc),\
                local_tz.localize(end_date).astimezone(timezone.utc)]

                
            #===================================================================
            # print start_date
            # print start_time
            #print end_time
            # 
            # 
            # print local_tz.localize(timezone.datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute, 0, 0)).astimezone(timezone.utc)
            # print local_tz.localize(timezone.datetime(start_date.year, start_date.month, start_date.day, end_time.hour, end_time.minute, 0, 0)).astimezone(timezone.utc)
            # 
            #===================================================================
            return [local_tz.localize(timezone.datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute, 0, 0)).astimezone(timezone.utc),\
                    local_tz.localize(timezone.datetime(start_date.year, start_date.month, start_date.day, end_time.hour, end_time.minute, 0, 0)).astimezone(timezone.utc)]
        
        if len(time_list)==8:
            '''
            start and end dates provided both, using Format2TimeString
            '''
            format2time = Format2TimeString(*time_list)
            start_date = Date(*[int(_x) for _x in format2time.start_date.split(".")])
            end_date = Date(*[int(_x) for _x in format2time.end_date.split(".")])
            start_time = Time(*[int(_x) for _x in format2time.start_time.split(':')])
            end_time = Time(*[int(_x) for _x in format2time.end_time.split(':')])
            
            return [local_tz.localize(timezone.datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute,0, 0)).astimezone(timezone.utc),\
                    local_tz.localize(timezone.datetime(end_date.year, end_date.month, end_date.day, end_time.hour, end_time.minute, 0,0)).astimezone(timezone.utc)]
        
        else:
            raise TimeParseError(time_string)
        
        
        
    def find_work_start_end_dates(self, time_set):
        '''
        returns (min_date, max_date)
        '''
        time_tuple = []
        for x in time_set:
            time_tuple += self.convert_to_python_datetime(x)
        return (min(time_tuple), max(time_tuple))
        
        
        

#make it class or instance method, place data in containers to minimise db requests
    def gen_notification_body(self,local_notification_obj, local_work_obj):
        '''
        Generate body and subject based on local_notification_obj and local_work_obj 
        '''
        #print "-> start lookup template"
        notification_template = filter(lambda _x: (_x.notification_type==local_notification_obj.notification_type and \
                                       _x.notificationtemplate_language==local_notification_obj.client.client_language), self.NotificationTemplates)[0]
        #NotificationTemplate.objects.get(notification_type = local_notification_obj.notification_type,\
        #print "<- end lookup template"#                                                         notificationtemplate_language = local_notification_obj.notification_client.client_language)
        
        
        if not notification_template:
            raise Exception("blah")
        else:
            pass
            #print notification_template.notificationtemplate_text
        
        
        outages_text = ""
        
        #print "-> start search MWs for notification"
        #MWs = filter(lambda _x: _x.mw_notification == local_notification_obj, self.MaintenanceWindows)
        
        MWs = local_notification_obj.mws
        MWs = sorted(MWs, key=lambda x: x.mw_start_date)
        #print "found MWs for notification", len(MWs)
        #print "<- end search MWs for notification"
        
        for MW in MWs:
            outages_text += "\n--" + MW.mw_start_date.astimezone(utc_tz).strftime('%d.%m.%Y %H:%M') + "-"+ MW.mw_end_date.astimezone(utc_tz).strftime('%d.%m.%Y %H:%M') + ' (UTC):'
            
            
            outages_objects = MW.outages#Outage.objects.filter(outage_mw=MW)
            
#TODO - outages must be grouped by type, after outage type - chanel list
#DONE
#NEW CODE
            outage_types_set = set([_x.outage_type for _x in outages_objects])
            for outage_type in outage_types_set:
                
                outage_template = filter(lambda _x: (_x.outagetemplate_language == local_notification_obj.client.client_language and \
                                         _x.outagetemplate_outagetype== outage_type), self.OutageTemplates)[0]
                outages_text += "\n"+ outage_template.outagetemplate_text
                same_type_outages = filter(lambda _x: _x.outage_type==outage_type, outages_objects)
                outages_text += "\n---\n"
                
                for same_type_outage in same_type_outages:
                    outages_text += same_type_outage.outage_circuit + "\n"
                outages_text += "---\n"
                
                #outage_type_template_text = 



#OLD CODE
#            for outage in outages_objects:
#                
#                outage_template = filter(lambda _x: (_x.outagetemplate_language == local_notification_obj.client.client_language and \
#                                         _x.outagetemplate_outagetype== outage.outage_type), self.OutageTemplates)[0]
#                #outage_template = OutageTemplate.objects.get(outagetemplate_language = local_notification_obj.notification_client.client_language,\
#                #                                             outagetemplate_outagetype = outage.outage_type)
#                
#                outage_template_text = outage_template.outagetemplate_text
#                outages_text += outage_template_text.replace("%circuit_name%",outage.outage_circuit) + "\n\n\n"
                
            #print "<- end search outages for MW"
        
        #print '-> start form body'
        notification_body = notification_template.notificationtemplate_text
        notification_body = notification_body.replace("%work_number%", local_work_obj.work_number)
        notification_body = notification_body.replace("%client_name%", local_notification_obj.client.client_display_name)
        
        
        
        work_region = filter(lambda _x: (_x.workregionlang == local_notification_obj.client.client_language and \
                             _x.workregion == local_work_obj.work_region), self.WorkRegionDescriptions)[0].workregdesc
        #WorkRegionDescription.objects.get(workregionlang=local_notification_obj.notification_client.client_language, workregion=local_notification_obj.notification_work.work_region).workregdesc
        
        
        work_location = filter(lambda _x: (_x.worklocationlang == local_notification_obj.client.client_language and \
                                            _x.worklocation == local_work_obj.work_region.region_location), self.WorkLocationDescriptions)[0].worklocdesc
        #WorkLocationDescription.objects.get(worklocationlang=local_notification_obj.notification_client.client_language, worklocation = local_notification_obj.notification_work.work_region.region_location).worklocdesc
        
        #work_type = filter
        
        notification_body = notification_body.replace("%work_location%", work_location)
        notification_body = notification_body.replace("%work_region%",work_region)
        notification_body = notification_body.replace("%work_type%", "work_type")#local_notification_obj.notification_work.work_type.objects.get(id=1).worktype_name)
        notification_body = notification_body.replace("%work_start_time%",local_work_obj.work_start_date.astimezone(utc_tz).strftime('%d.%m.%Y %H:%M'))
        notification_body = notification_body.replace("%work_end_time%",local_work_obj.work_end_date.astimezone(utc_tz).strftime('%d.%m.%Y %H:%M'))
        notification_body = notification_body.replace("%outages_block%", outages_text)
        
        notification_subject = notification_template.notificationtemplate_subject.replace("%work_number%",local_work_obj.work_number)
        
        #print '<- end form body'
        return notification_subject,notification_body
#if __name__ == "__main__":
#    s = ""
#    
#    with open("16.10-29.10-1.csv", 'rt') as csv_file_desc:
#        MyContainer = WorkContainer(csv_file_desc)
#        MyContainer.parse()