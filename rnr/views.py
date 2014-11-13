

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
#from django.core.servers.basehttp import FileWrapper

#from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from forms import UploadFileForm, NewRecordForm, RecordsForm, ClientForm, WorkForm, NotificationForm
from django.template import RequestContext, Context

from models import DictRecord, Client, Contact, Language, WorkType, Work, \
NotificationTemplate, Notification, Outage, OutageType, Location, Region, \
MaintenanceWindow, OutageTemplate, NotificationType, NotificationState, WorkTypeDescription,\
WorkLocationDescription, WorkRegionDescription, NotificationTypeDescription, OutageTypeDescription,\
NotificationStateDescription
from processor.csvfile import CSVProcessor, CSVParseOptions
from django.core.exceptions import ValidationError
import json


import simplejson
from django.core import serializers
import datetime
import pytz
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from processor.emails import EmailProcessor
from processor.tmp_csv_proc import WorkContainer
from processor.errors import RecordParseError
from django.db import transaction
from django.db.models import Q

#    csv_row[time_row_number] = time_string.encode('1251')

local_tz = timezone.get_current_timezone()
utc_tz = timezone.utc

def set_language(request):
    if request.method == "GET":
        #request.META["HTTP_REFERER"]
        
        lang = request.GET.get('lang', None)
        response = HttpResponseRedirect(request.META["HTTP_REFERER"])
        print "got language change request", lang
        if lang == "ru":
            response.set_cookie(key="lang", value="ru", max_age=365*24*60*60, expires=None, path='/')
        else:
            response.set_cookie(key="lang", value="en", max_age=365*24*60*60, expires=None, path='/')
        return response
        

def rnr_home(request):
    return render_to_response('rnr_home.html')

def rnr_works(request):
    
    #lang = request.COOKIES.get('lang', None)
    #if lang == 'ru':
    #    return render_to_response('rnr_works_ru.html')
    #else:
    #    return render_to_response('rnr_works.html')
    return render_to_response('rnr_works.html')




def test_bootstrap(request):
    return render_to_response('test_bootstrap.html')
def csv_parser (request):
    '''
    main parser page
    '''
    if request.method == "GET":
        
        def_options = CSVParseOptions()
        upload_file_form = UploadFileForm(def_options.options)
        all_records_form = RecordsForm()
        new_record_form = NewRecordForm()
        dictrecords = DictRecord.objects.all()
        
        return render_to_response('csv_processor.html', {'all_records_form':all_records_form,  \
                                               'upload_file_form':upload_file_form, \
                                               'new_record_form':new_record_form, \
                                               'dictrecords':dictrecords }, context_instance=RequestContext(request))
        
    else:
        return HttpResponseRedirect("/rnr/csv_parser/")

def csv_process(request):
    '''
    POST request to parse uploaded csv file
    '''
    
    if request.method == "POST":
        
        upload_file_form = UploadFileForm(request.POST, request.FILES)
        
        if upload_file_form.is_valid():
            
            input_file = upload_file_form.cleaned_data['input_file']
            
            output_file = HttpResponse ( content_type = 'txt/csv')
            output_file['Content-Disposition'] = 'attachment; filename=output.csv'
                        
            #Load options from form
            csv_opt = CSVParseOptions()
            csv_opt.options.update(upload_file_form.cleaned_data)
            
            csv_processor = CSVProcessor( input_file, output_file, csv_opt )
            csv_processor.process_file()
            
            return output_file
        
#             return HttpResponseRedirect("/rnr/csv_process/")
        else:
            return HttpResponseRedirect("/rnr/csv_process/")
        
    else:
        return HttpResponseRedirect("/rnr/csv_parser/")
        


#    resp = HttpResponse( mimetype = 'text/csv' )
#    resp['Content-Disposition'] = 'attachment; filename=test.csv'
#    import csv
#    TRG = csv.writer ( resp )
#    TRG.writerow( ['blah', 'blablabla']  )
#    for x in range(10):
#        TRG.writerow( [str(x), str(x*2) ] )
#    return resp

def add_new_record( request ):
    if request.method == "POST":
        new_record_form = NewRecordForm(request.POST)
        if new_record_form.is_valid():
            init_word  = new_record_form.cleaned_data['init_word']
            replace_word = new_record_form.cleaned_data['replace_word']
            new_record = DictRecord(init_word = init_word, replace_word=replace_word)
            new_record.save()
            return HttpResponseRedirect("/rnr/csv_parser/")
    else:
        return HttpResponseRedirect('/rnr/csv_parser/')

def delete_record( request ):
    if request.method == "POST":
        del_record_form = RecordsForm(request.POST)
        if del_record_form.is_valid():
            del_list = del_record_form.cleaned_data['Records']
            for x in del_list:
                _tmp_obj = DictRecord.objects.get(init_word = x).delete()

            return HttpResponseRedirect("/rnr/csv_parser/")
    else:
        return HttpResponseRedirect("/rnr/csv_parser/")
    


def rnr_clients(request):
    if request.method == "GET":
        return render_to_response('rnr_clients.html')
        
        
def rnr_notifications(request):
    print request.GET
    #work_slug = request.GET["work_slug"]
    #if work_slug:
    #    notifications = Notification.objects.filter(notification_work__slug=work_slug).values("slug", "notification_client__client_name", "notification_type__notificationtype_name", "notification_state__notificationstate_name", )
    #    
    #    
    #    notifications = simplejson.dumps(list(notifications))
    #    response = HttpResponse(notifications, content_type='application/json')
    #    return response
    
    
    return render_to_response('rnr_notifications.html')
        

def rnr_clients_old(request):
    if request.method == "POST":
        cl_form = ClientForm()
        return render_to_response('clients.html',{'cl_form':cl_form}, context_instance=RequestContext(request))
    if request.method == "GET":
        clients = Client.objects.all()
        language_objects = Language.objects.all()
        works = Work.objects.all()
        outage_types = OutageType.objects.all()
        notification_templates = NotificationTemplate.objects.all()
        work_types = WorkType.objects.all()
        work_locations = Location.objects.all()
        client_list = []
        for client in clients:
            contacts = Contact.objects.filter(client=client).values('contact_email', 'slug')
            client.contacts=contacts
#             print contacts
            language = Language.objects.filter(client=client).values('language_name','slug')
            client.language = language
            client_list.append(client)
#             work_types = WorkType.objects.values('worktype_name','slug')
#             print work_types
#         print dir(clients)
        return render_to_response('clients.html',locals(), context_instance=RequestContext(request))
    

def get_languages_all_json(request):
    if request.method == "GET":
        languages = Language.objects.values('slug','language_name')
        languages = simplejson.dumps(list(languages))
        response = HttpResponse(languages, content_type='application/json')
        return response

def clients_get_all_json( request ):
    #cl_form = ClientForm(request.POST)
    #clients = Client.objects.raw("select rnr_client.id, rnr_client.slug as client_slug, rnr_language.slug as language_slug, rnr_client.client_name, rnr_language.language_name from rnr_client inner join rnr_language on rnr_client.client_language_id = rnr_language.id;")
    client_objs = Client.objects.values('slug', 'client_name', 'client_language__slug','client_language__language_name')  
#     Client.objects.extra()
#     c = serializers.serialize('json', clients)
    
    
    #[client_slug:{'name':}]
    clients = []
    for client_obj in client_objs:
        
        client_slug = client_obj.pop('slug')
        
        
        contact_objs = Contact.objects.filter(client__slug=client_slug).values('slug', 'contact_email')
#        print type(contact_objs)
#        print type(client_objs)
#         cont_json = simplejson.dumps({'emails':list(contact_objs})
        client_data={'client_slug':client_slug, 'attribs':client_obj, 'contacts':list(contact_objs)}
        
        clients.append(client_data)
#         
#         [c for c in contact_objs]
            
    
#    print clients
#     print contacts
#     print dir(clients[0])
#     d = []
#     for _client in clients:
#         contacts = Contact.objects.raw("select id, contact_email, slug from rnr_contact where rnr_contact.client_id_id ="+str(_client.id))
#         c = [{'contact_slug':contact.slug, 'contact_email':contact.contact_email} for contact in contacts]
#         l={_client.client_slug:\
#            {'client_name':_client.client_name, 
#             'client_language':_client.language_name,
#             'language_slug':_client.language_slug ,'contacts':c}}
#         d.append(l)
    
    l = sorted(clients, reverse=False, key=lambda x: x["attribs"]["client_name"])
    clients = simplejson.dumps(l)
    
    response = HttpResponse(clients, content_type='application/json')
    
    
#    response['Content-Type'] = "application/json"
#    response.write("[{'attribs': {'client_language__language_name': u'English', 'client_name': u'BT', 'client_language__slug': u'a9a4754BAccD'}, 'client_slug': u'b0aeAFC923bD', 'contacts': [{'contact_email': u'bt@bt.com', 'slug': u'F94ECa3226B2'}, {'contact_email': u'root@bt.com', 'slug': u'cb3C1f46E725'}]}, {'attribs': {'client_language__language_name': u'English', 'client_name': u'Telia Sonera', 'client_language__slug': u'a9a4754BAccD'}, 'client_slug': u'BA8CeC5DFD8e', 'contacts': [{'contact_email': u'admin@telia.com', 'slug': u'F2dAc015db4a'}, {'contact_email': u'admin@telia.net', 'slug': u'Aae1c3c805D4'}, {'contact_email': u'root@telia.com', 'slug': u'1accA0A7Ff8E'}]}]")
    return response

def get_work_types_json( request ):
    if request.method == 'GET':
        work_types = WorkType.objects.values('slug', 'worktype_name')
#        l=[]
#        for work_type in work_types:
#            l.append({})
        work_types = simplejson.dumps(list(work_types))
        print work_types
        response = HttpResponse(work_types, content_type='application/json')
        return response

def get_works_json( request ):
    '''
TODO    minimize db requests
    '''
    
    if request.method == 'GET':
#       work_objects = Work.objects.all()#('slug', 'work_number', 'work_type__worktype_name', 'work_circuit', 'work_start_date', 'work_end_date')
        
        work_filter_number = request.GET["work_filter_number"]
        work_filter_pending = request.GET["work_filter_pending"]
        work_filter_upcoming = request.GET["work_filter_upcoming"]
        work_filter_completed = request.GET["work_filter_completed"]
        
        work_filter_dict={"work_filter_number":work_filter_number,\
                          "work_filter_pending":work_filter_pending,\
                          "work_filter_upcoming":work_filter_upcoming,
                          "work_filter_completed":work_filter_completed}
        
        print simplejson.dumps(work_filter_dict)
        
        
        query_time = timezone.now()
        
        if work_filter_pending == "true":
            q_obj_p = Q(work_start_date__lte = query_time) & Q(work_end_date__gt = query_time)
        else:
            q_obj_p = Q()
            
        if work_filter_upcoming == "true":
            q_obj_u = Q(work_start_date__gt = query_time)
        else:
            q_obj_u = Q()
            
        if work_filter_completed == "true":
            q_obj_c = Q(work_end_date__lt = query_time)
        else:
            q_obj_c = Q()
        
        if work_filter_number:
            #work_date = datetime.date(*[int(x) for x in work_filter_number.split("-")])
            #q_obj_df = Q(work_added__gte = work_date)
            q_obj_df = Q(work_number__icontains = work_filter_number)
            
        else:
            q_obj_df = Q()
        
            
        work_objects = Work.objects.filter(q_obj_p | q_obj_u | q_obj_c).filter(q_obj_df)
        print work_objects.query
            #work_objects = work_objects.filter(work_start_date__lte = timezone.now()).filter(work_end_date__gt = timezone.now())
#            print work_objects.query
#            print work_objects
        #if work_filter_pending == "true":
        #    work_objects = work_objects.filter(work_start_date__gte = timezone.now()).filter(work_end_date__gt = timezone.now())
       
        l=[]
        
        
        
        lang = request.COOKIES.get('lang', None)
        print "work requested",lang
        
        for work in work_objects:
            d={}
            d["slug"] = work.slug
            d["work_number"] = work.work_number
            if lang == 'ru':
                lang_obj = Language.objects.get(language_name="Russian")
                d["work_type"] = WorkTypeDescription.objects.get(worktype=work.work_type, worktypelang=lang_obj).worktypedesc
                d["work_region"] = WorkRegionDescription.objects.get(workregionlang = lang_obj, workregion=work.work_region).workregdesc
                
            else:
                lang_obj = Language.objects.get(language_name="English")
                d["work_type"] = WorkTypeDescription.objects.get(worktype=work.work_type, worktypelang=lang_obj).worktypedesc
                d["work_region"] = WorkRegionDescription.objects.get(workregionlang = lang_obj, workregion=work.work_region).workregdesc
            
            
            d["work_circuit"] = work.work_circuit
            notifications = Notification.objects.filter(notification_work__slug=work.slug)
            
            init_notifications = notifications.filter(notification_state__notificationstate_name="init", notification_type__notificationtype_name="notification").count()
            sent_notifications = notifications.filter(notification_state__notificationstate_name="sent", notification_type__notificationtype_name="notification").count()
            sent_error_notifications = notifications.filter(notification_state__notificationstate_name="sent_error", notification_type__notificationtype_name="notification").count()
            
            init_cancel_notifications = notifications.filter(notification_state__notificationstate_name="init", notification_type__notificationtype_name="cancel").count()
            sent_cancel_notifications = notifications.filter(notification_state__notificationstate_name="sent", notification_type__notificationtype_name="cancel").count()
            sent_error_cancel_notifications = notifications.filter(notification_state__notificationstate_name="sent_error", notification_type__notificationtype_name="cancel").count()
                        
            d["init_notifications"] = init_notifications
            d["sent_notifications"] = sent_notifications
            d["sent_error_notifications"] = sent_error_notifications
            
            d["init_cancel_notifications"] = init_cancel_notifications
            d["sent_cancel_notifications"] = sent_cancel_notifications
            d["sent_error_cancel_notifications"] = sent_error_cancel_notifications
            
            if work.work_state != "Canceled":
                if work.work_start_date.astimezone(local_tz) > timezone.now() < work.work_end_date.astimezone(local_tz):
                    d["work_state"] = "Upcoming"
                if work.work_start_date.astimezone(local_tz) <= timezone.now() <= work.work_end_date.astimezone(local_tz):
                    d["work_state"] = "Pending"
                if work.work_start_date.astimezone(local_tz) < timezone.now() > work.work_end_date.astimezone(local_tz):
                    d["work_state"] = "Completed"
                
            
            d["work_start_date"] = work.work_start_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M')
            d["work_end_date"] = work.work_end_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M')
            #print d
            l.append(d)
        
        #=======================================================================
        # l1=[]
        # 
        # if work_filter_pending == "true":
        #     pending_works_objects = filter(lambda _x: _x["work_state"]=="Pending", l)
        #     print len(pending_works_objects)
        #     l1 += pending_works_objects
        # if work_filter_upcoming == "true":
        #     upcoming_works_objects = filter(lambda _x: _x["work_state"]=="Upcoming", l)
        #     print len(upcoming_works_objects)
        #     l1 += upcoming_works_objects
        # if work_filter_completed == "true":
        #     completed_works_objects = filter(lambda _x: _x["work_state"]=="Completed", l)
        #     l1 += completed_works_objects
        # #l1 = pending_works_objects + upcoming_works_objects + completed_works_objects
        # print len(l1)
        #=======================================================================
#TODO - fix the bug with sort by date (sorting based on day number only)
        l = sorted(l, reverse=True, key=lambda x: x["work_start_date"])
        works = simplejson.dumps(l)
        response = HttpResponse(works, content_type='application/json')
        response.set_cookie(key="filter_works", value=simplejson.dumps(work_filter_dict), max_age=365*24*60*60, expires=None, path='/')
        
        
        
        return response
    
def get_work_name_json(request):
    if request.method == 'GET':
        work_slug = request.GET["slug"]
        work = Work.objects.get(slug=work_slug)
        work = simplejson.dumps({"work_number":work.work_number})
        response = HttpResponse(work, content_type='application/json')
        return response
    
#def get_client_names_json(request):
#    if request.method == 'GET':
#        clients = Client.objects.all().values_list('client_name', flat=True)
#        clients = simplejson.dumps(list(clients))
#        print clients
#        response = HttpResponse(clients, content_type='application/json')
#        return response
    
def get_client_names_json(request):
    if request.method == 'GET':
        clients = Client.objects.all().values('slug','client_name')
        clients = simplejson.dumps(list(clients))
        #print clients
        response = HttpResponse(clients, content_type='application/json')
        return response
    
    
def get_worktypes_all_json(request):
    if request.method == 'GET':
        lang = request.COOKIES.get('lang', None)
        if lang == 'ru':
            lang_object = Language.objects.get(language_name='Russian')
            work_types = WorkTypeDescription.objects.filter(worktypelang=lang_object).values("worktype__slug","worktypedesc")
        else:
            lang_object = Language.objects.get(language_name='English')
            work_types = WorkTypeDescription.objects.filter(worktypelang=lang_object).values('worktype__slug', 'worktypedesc')
        
        work_types = simplejson.dumps(list(work_types))
        response = HttpResponse(work_types, content_type='application/json')
        return response
    
def get_locations_all_json( request ):
    if request.method == 'GET':
        lang = request.COOKIES.get('lang', None)
        if lang == 'ru':
            lang_object = Language.objects.get(language_name='Russian')
            locations = WorkLocationDescription.objects.filter(worklocationlang=lang_object).values("worklocation__slug", "worklocdesc")
        else:
            lang_object = Language.objects.get(language_name='English')
            locations = WorkLocationDescription.objects.filter(worklocationlang=lang_object).values("worklocation__slug", "worklocdesc")
#        print locations
        locations = simplejson.dumps(list(locations))
        response = HttpResponse(locations, content_type='application/json')
        return response
    
def get_regions_json( request ):
    if request.method == 'GET':
        location_slug = request.GET["location_slug"]
        lang = request.COOKIES.get('lang', None)
        if lang == 'ru':
            lang_object = Language.objects.get(language_name='Russian')
            regions = WorkRegionDescription.objects.filter(workregionlang = lang_object, workregion__region_location__slug=location_slug).values('workregion__slug', 'workregdesc')
        else:
            lang_object = Language.objects.get(language_name='English')
            regions = WorkRegionDescription.objects.filter(workregionlang = lang_object, workregion__region_location__slug=location_slug).values('workregion__slug', 'workregdesc')
        #regions = Region.objects.filter(region_location__slug=location_slug).values('slug', 'region_name')
        regions = simplejson.dumps(list(regions))
        response = HttpResponse(regions, content_type='application/json')
        return response
    
def get_notifications_json( request ):
    if request.method == 'GET':
        work_slug = request.GET["work_slug"]
        lang = request.COOKIES.get('lang', None)
        
        notifications = Notification.objects.filter(notification_work__slug=work_slug).values("slug", "notification_client__client_name", "notification_type__notificationtype_name", "notification_state__notificationstate_name")
#        print type(notifications)
        
#        print request.GET
        if "notification_type" in request.GET:
            notification_type = request.GET["notification_type"]
            if notification_type:
                notifications = notifications.filter(notification_type__notificationtype_name = notification_type).values("slug", "notification_client__client_name", "notification_type__notificationtype_name", "notification_state__notificationstate_name")
#            print notifications
#            print notification_type
            
        if "notification_state" in request.GET:
            notification_state = request.GET["notification_state"]
            if notification_state:
                notifications = notifications.filter(notification_state__notificationstate_name = notification_state).values("slug", "notification_client__client_name", "notification_type__notificationtype_name", "notification_state__notificationstate_name")
#            print notification_state
            
        l = sorted(list(notifications), reverse=False, key=lambda x: x["notification_client__client_name"])
        
        if lang == 'ru':
            lang_object = Language.objects.get(language_name='Russian')
            for _x in l:
                if _x["notification_state__notificationstate_name"] == "init":
                    _x["state_class"] = "info"
                if _x["notification_state__notificationstate_name"] == "sent":
                    _x["state_class"] = "success"
                if _x["notification_state__notificationstate_name"] == "sent_error":
                    _x["state_class"] = "error"
                    
                if _x["notification_type__notificationtype_name"] == "cancel":
                    _x["type_class"] = "info"
                    #- _x["notification_type__notificationtype_name"] = "Otmena"
                    
                if _x["notification_type__notificationtype_name"] == "notification":
                    # _x["notification_type__notificationtype_name"] = "Opoveschenie"
                    _x["type_class"] = "success"
                    
                _x["notification_state__notificationstate_name"] = NotificationStateDescription.objects.get(notificationstatelang=lang_object,notificationstate__notificationstate_name=_x["notification_state__notificationstate_name"]).outagetypedesc
                _x["notification_type__notificationtype_name"] = NotificationTypeDescription.objects.get(notificationtypelang = lang_object, notificationtype__notificationtype_name=_x["notification_type__notificationtype_name"]).notificationtypedesc
        else:
            lang_object = Language.objects.get(language_name='English')
            for _x in l:
                if _x["notification_state__notificationstate_name"] == "init":
                    _x["state_class"] = "info"
                if _x["notification_state__notificationstate_name"] == "sent":
                    _x["state_class"] = "success"
                if _x["notification_state__notificationstate_name"] == "sent_error":
                    _x["state_class"] = "error"
                    
                if _x["notification_type__notificationtype_name"] == "cancel":
                    _x["type_class"] = "info"
                    
                if _x["notification_type__notificationtype_name"] == "notification":
                    _x["type_class"] = "success"
                    
                _x["notification_state__notificationstate_name"] = NotificationStateDescription.objects.get(notificationstatelang=lang_object,notificationstate__notificationstate_name=_x["notification_state__notificationstate_name"]).outagetypedesc
                _x["notification_type__notificationtype_name"] = NotificationTypeDescription.objects.get(notificationtypelang = lang_object, notificationtype__notificationtype_name=_x["notification_type__notificationtype_name"]).notificationtypedesc
#        print l
        notifications = simplejson.dumps(l)
        response = HttpResponse(notifications, content_type='application/json')
        return response

def get_notification_type_all_json(request):
    if request.method == 'GET':
        lang = request.COOKIES.get('lang', None)
        
        
        if lang == 'ru':
            lang_object = Language.objects.get(language_name='Russian')
            notification_types = NotificationTypeDescription.objects.filter(notificationtypelang=lang_object).values("notificationtype__slug","notificationtypedesc")
        else:
            lang_object = Language.objects.get(language_name='English')
            notification_types = NotificationTypeDescription.objects.filter(notificationtypelang=lang_object).values("notificationtype__slug","notificationtypedesc")
        #notification_types = NotificationType.objects.values('slug', 'notificationtype_name')
        notification_types = simplejson.dumps(list(notification_types))
        response = HttpResponse(notification_types, content_type='application/json')
        return response
    
def get_outage_type_all_json(request):
    if request.method == 'GET':
        lang = request.COOKIES.get('lang', None)
        if lang == 'ru':
            lang_object = Language.objects.get(language_name='Russian')
            outage_types = OutageTypeDescription.objects.filter(outagetypelang=lang_object).values("outagetype__slug", "outagetypedesc")
        else:
            lang_object = Language.objects.get(language_name='English')
            outage_types = OutageTypeDescription.objects.filter(outagetypelang=lang_object).values("outagetype__slug", "outagetypedesc")
            
        outage_types = simplejson.dumps(list(outage_types))
        response = HttpResponse(outage_types, content_type='application/json')
        return response

def get_outages_json( request ):
    if request.method == 'GET':
        notification_slug=request.GET["notification_slug"]
        outages = Outage.objects.filter(outage_notification__slug=notification_slug).values('slug', 'outage_circuit','outage_start_date', 'outage_end_date','outage_type__outagetype_name')
        for outage in outages:
            outage['outage_start_date'] = outage['outage_start_date'].strftime('%d.%m.%Y %H:%M')
            outage['outage_end_date'] = outage['outage_end_date'].strftime('%d.%m.%Y %H:%M')
        outages = simplejson.dumps(list(outages))
        response = HttpResponse(outages, content_type='application/json')
        return response

@csrf_exempt
def add_new_client( request ):
    '''
    add new client
    '''
    if request.is_ajax():
        if request.method == 'POST':
            new_client_form = ClientForm(request.POST)
            if new_client_form.is_valid():
                client_name = new_client_form.cleaned_data['client_name']
                client_language = new_client_form.cleaned_data['client_language']
                client_contacts = new_client_form.cleaned_data['client_emails']
                shiny_new_client = Client(client_name = client_name, client_language=client_language)
                shiny_new_client.save()
                for contact in client_contacts:
                    new_contact = Contact(client=shiny_new_client, contact_email=contact)
                    new_contact.save()
                return HttpResponse('{"errors": [], "success": true}',content_type='application/json')
            
            else:
                errors = {}
                for error in new_client_form.errors.items():
                    #field name and error
                    errors[error[0]] = error[1]
                
                return HttpResponse(simplejson.dumps({"errors": errors, "success": False}) ,content_type='application/json')
    return HttpResponse("OK")

@csrf_exempt
def del_notification(request):
    '''
    delete notification based on slug
    '''
    if request.method == 'POST':
        notification_slug = request.POST["notification_slug"]
        notification_obj = Notification.objects.get(slug=notification_slug)
        notification_obj.delete()
        return HttpResponse("OK")
        

def del_client(request):
    '''
    remove client, remove all contacts, remove notifications.
    '''
    if request.method == 'GET':
        client_slug = request.GET['client_slug']
        client_obj = Client.objects.get(slug = client_slug)
        client_obj.delete()
        return HttpResponse("OK")
    
def del_contact(request):
    '''
    remove contact
    '''
    if request.method == 'POST':
        contact_slug = request.POST['contact_slug']
        contact_obj = Contact.objects.get(slug = contact_slug)
        
        response = {"errors": [], "success": True}
        
        
        try:
            contact_obj.delete()
        except ValidationError as e:
            response = {'errors':"This address is last and cannot be deleted!","success":False}
            return HttpResponse(simplejson.dumps(response), content_type='application/json')
        
        return HttpResponse("OK")
    
@csrf_exempt
def add_new_work( request ):
    
    if request.is_ajax():
        if request.method == 'POST':
            new_work_form = WorkForm(request.POST)
            if new_work_form.is_valid():
                
                work_number = new_work_form.cleaned_data['work_number']
                work_type = new_work_form.cleaned_data['work_type']
                work_circuit = new_work_form.cleaned_data['work_circuit']
                work_start_datetime = new_work_form.cleaned_data['work_start_datetime']
                work_end_datetime = new_work_form.cleaned_data['work_end_datetime']
                work_region = Region.objects.get(slug=new_work_form.cleaned_data['work_region'])
                
                print work_start_datetime
                work_start_datetime = work_start_datetime.astimezone(utc_tz)
                work_end_datetime = work_end_datetime.astimezone(utc_tz)
                
                print work_start_datetime
                
                work_added = timezone.now()
                
                
                shiny_new_work = Work(work_number=work_number, work_type=work_type, \
                                      work_circuit = work_circuit, work_start_date = work_start_datetime,\
                                      work_end_date = work_end_datetime, work_region = work_region, work_added=work_added)
                shiny_new_work.save()                
                return HttpResponse("OK")
            else:
                print new_work_form.errors.as_text()
                return HttpResponse(new_work_form.errors.as_text())
#             print new_client_form.cleaned_data
#             print 'Raw Data: "%s"' % request.body
            print new_work_form.errors
    return HttpResponse("OK")

@csrf_exempt
def add_new_notification( request ):
    
    if request.is_ajax():
        if request.method == 'POST':
            new_notification_form = NotificationForm(request.POST)
            print request.POST
            if new_notification_form.is_valid():
                
                notification_client = new_notification_form.cleaned_data['notification_client']
                notification_work = new_notification_form.cleaned_data['notification_work']
                notification_template = new_notification_form.cleaned_data['notification_template']
                print new_notification_form.cleaned_data
                notification_complete_text = new_notification_form.cleaned_data['notification_complete_text']
                print notification_complete_text
                print 111
                shiny_new_notification = Notification(notification_client=notification_client,\
                                                      notification_work=notification_work,\
                                                      notification_template = notification_template,\
                                                      notification_complete_text = notification_complete_text)
                shiny_new_notification.save()
                return HttpResponse("OK")
            else:
                print new_notification_form.errors.as_text()
                return HttpResponse(new_notification_form.errors.as_text())
#             print new_client_form.cleaned_data
#             print 'Raw Data: "%s"' % request.body
            print new_notification_form.errors
    return HttpResponse("OK")

@csrf_exempt
def send_notification(request):
    if request.method == 'POST':
        notification_slug = request.POST["notification_slug"]
        notification_obj = Notification.objects.get(slug=notification_slug)
        
        e_processor = EmailProcessor()
        e_processor.add_to_queue(notification_obj)
        e_processor.send_queue()
        
        notif_sent_state = NotificationState.objects.get(notificationstate_name='sent')
        notification_obj.notification_state = notif_sent_state
        notification_obj.save()
        return HttpResponse("OK")

@csrf_exempt
def send_all_notifications(request):
    '''
        var send_notif_error = $("#send_error_messages").prop('checked');
        var send_notif_init = $("#send_error_messages").prop('checked');
        var send_notif_sent = $("#send_error_messages").prop('checked');
        
        var send_cancel_error = $("#send_error_messages").prop('checked');
        var send_cancel_init = $("#send_error_messages").prop('checked');
        var send_cancel_sent = $("#send_error_messages").prop('checked');
    
    '''
    if request.method == 'POST':
        work_slug = request.POST["work_slug"]
        send_notif_error = request.POST["send_notif_error"]
        send_notif_init = request.POST["send_notif_init"]
        send_notif_sent = request.POST["send_notif_sent"]
        
        send_cancel_error = request.POST["send_cancel_error"]
        send_cancel_init = request.POST["send_cancel_init"]
        send_cancel_sent = request.POST["send_cancel_sent"]
        
        
        #if send_notif_error == "true":
            #Q(work_start_date__lte = query_time) & Q(work_end_date__gt = query_time)
        #    send_notif_error_Q = Q()
        
        #notification_types = requset.POST["notifications_types"]
        work_django_obj = Work.objects.get(slug=work_slug)
        matched_notifications = Notification.objects.filter(notification_work = work_django_obj)
        
        
        e_processor = EmailProcessor()
        
        for notification_dj_obj in matched_notifications:
            e_processor.add_to_queue(notification_dj_obj)
        
        e_processor.send_queue()
            
        response = HttpResponse(simplejson.dumps({'success':True}), content_type='application/json')
            
        return response


def view_notification(request):
    if request.method == 'GET':
        notification_slug = request.GET["notification_slug"]
        notification_obj = Notification.objects.get(slug=notification_slug)
        notification_obj = simplejson.dumps({'notification_complete_text':notification_obj.notification_complete_text,\
                                             'notification_subject':notification_obj.notification_subject})
        response = HttpResponse(notification_obj, content_type='application/json')
        return response


def cancel_work(request):
    if request.method == 'POST':
        work_slug = request.POST["work_slug"]
        work_django_obj = Work.objects.get(slug=work_slug)
        return HttpResponse("Hi there!")
    
def delete_work(request):
    if request.method == 'POST':
        work_slug = request.POST["work_slug"]
        work_django_obj = Work.objects.get(slug=work_slug)
        work_django_obj.delete()
        return HttpResponse(simplejson.dumps({"success":True}))


@csrf_exempt
def save_notification(request):
    '''
    save notification, MW, outages in base
    '''
    if request.is_ajax():
        if request.method == 'POST':
            my_shiny_new_object = json.loads(request.POST["test"])
            
            work_slug = my_shiny_new_object["work_slug"]
            client_slug = my_shiny_new_object["client_slug"]
            notification_type_slug = my_shiny_new_object["notification_type_slug"]
            notification_text = request.POST["notification_text"]
            notification_subject = request.POST["notification_subject"]
            
            client_obj = Client.objects.get(slug=client_slug)
            work_obj = Work.objects.get(slug=work_slug)
            notification_type_obj = NotificationType.objects.get(slug=notification_type_slug)
            
            notification_obj=Notification.objects.create(notification_work=work_obj, notification_client=client_obj,\
            notification_type=notification_type_obj, notification_complete_text=notification_text, notification_subject = notification_subject)
            notification_obj.save()
        return HttpResponse("ok")


@csrf_exempt
def update_notification(request):
    '''
    Updates body and subject of notification
    '''
    if request.method == 'POST':
        new_subject = request.POST["message_subject"]
        new_body = request.POST["message_body"]
        notification_slug = request.POST["notification_slug"]
        notif_dj_obj = Notification.objects.get(slug=notification_slug)
        notif_dj_obj.notification_subject = new_subject
        notif_dj_obj.notification_complete_text = new_body
        notif_dj_obj.save()
        return HttpResponse("ok")
        
    
    
@csrf_exempt    
def gen_cancel(request):
    if request.method == 'POST':
        work_slug = request.POST["work_slug"]
        notification_type_obj = NotificationType.objects.get(notificationtype_name='cancel')
        clients = Client.objects.filter(notification__notification_work__slug = work_slug)#.filter(~Q(notification__notification_type = notification_type_obj))
        work_obj = Work.objects.get(slug=work_slug)
        
        
        for client in clients:
            notification_template_obj = NotificationTemplate.objects.get(notification_type = notification_type_obj,\
                                                                     notificationtemplate_language = client.client_language)
            notification_body = notification_template_obj.notificationtemplate_text
            notification_body = notification_body.replace("%work_number%", work_obj.work_number)
            notification_body =notification_body.replace("%client_name%", client.client_name)
            notification_subject = notification_template_obj.notificationtemplate_subject
            notification_subject = notification_subject.replace("%work_number%", work_obj.work_number)
            
            notif_obj = Notification(notification_work = work_obj, notification_client=client, notification_type=notification_type_obj,\
                                     notification_subject = notification_subject, notification_complete_text=notification_body)
            notif_obj.save()
    return HttpResponse("ok")


    
@csrf_exempt
def gen_notification(request):
    '''
    notification slug as input, full notification text as output.
%work_number%
%work_location%
%work_region%
 %work_type%
%work_start_time%
%work_end_time%
%client_name%
%outages_block%
    '''
    if request.method == 'GET':
        notification_slug=request.GET["notification_slug"]
        notification = Notification.objects.get(slug=notification_slug)
        work = Work.objects.get(slug=notification.notification_work.slug)
        maintenance_windows = MaintenanceWindow.objects.filter(mw_notification = notification)
        notification_language = notification.notification_client.client_language
        client_name = notification.notification_client.client_name
        notification_template = NotificationTemplate.objects.get(notification_type = notification.notification_type,notificationtemplate_language = notification_language)
        
        
        outages_text = ""
        for maintenance_window in maintenance_windows:
            outages_text += maintenance_window.mw_start_date.strftime('%d.%m.%Y %H:%M') + " - " + maintenance_window.mw_end_date.strftime('%d.%m.%Y %H:%M') + "\n\n"
            outages = Outage.objects.filter(outage_mw = maintenance_window)
            for outage in outages:
                
                outage_template = OutageTemplate.objects.get(outagetemplate_language = notification_language, outagetemplate_outagetype = outage.outage_type)
                outage_template_text = outage_template.outagetemplate_text
                outages_text += outage_template_text.replace("%circuit_name%",outage.outage_circuit) + "\n\n\n"
                
                          
        notification_body = notification_template.notificationtemplate_text
        notification_body = notification_body.replace("%work_number%", work.work_number)
        notification_body = notification_body.replace("%client_name%", client_name)
        
        work_location = WorkLocationDescription.objects.get(worklocationlang=notification_language, worklocation = notification.notification_work.work_region.region_location)
        work_region = WorkRegionDescription.objects.get(workregionlang=notification_language, workregion=notification.notification_work.work_region)
        
        notification_body = notification_body.replace("%work_location%", work_location)
        notification_body = notification_body.replace("%work_region%",work_region)
        
        
        notification_body = notification_body.replace("%work_type%",notification.notification_work.work_type.worktype_name)
        notification_body = notification_body.replace("%work_start_time%",notification.notification_work.work_start_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M'))
        notification_body = notification_body.replace("%work_end_time%",notification.notification_work.work_end_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M'))
        notification_body = notification_body.replace("%outages_block%", outages_text)
        
        notification_subject = notification_template.notificationtemplate_subject.replace("%work_number%",work.work_number)
        
        
        
        response = HttpResponse(notification_body)
        
        
        return response
    
    if request.method == 'POST':
        if request.is_ajax():
            my_shiny_new_object = json.loads(request.POST["test"])
            
            work_slug = my_shiny_new_object["work_slug"]
            client_slug = my_shiny_new_object["client_slug"]
            notification_type_slug = my_shiny_new_object["notification_type_slug"]
            #print work_slug
            #print client_slug
            
            client_obj = Client.objects.get(slug=client_slug)
            work_obj = Work.objects.get(slug=work_slug)
            notification_type_obj = NotificationType.objects.get(slug=notification_type_slug)
            notification_language = client_obj.client_language
            
            work_number = work_obj.work_number
            client_name = client_obj.client_name
            work_location = work_obj.work_region.region_location.location_name
            work_region = work_obj.work_region.region_name
            work_type = WorkTypeDescription.objects.get(worktypelang=notification_language, worktype=work_obj.work_type).worktypedesc
            
            outages_text = ""
            notification_template = NotificationTemplate.objects.get(notification_type = notification_type_obj,notificationtemplate_language = notification_language)
        
            
            #print notification_type_slug
            #print my_shiny_new_object["MW"]

#TODO Use list join, not +="\n"
            
            for maintenance_window in my_shiny_new_object["MW"]:
                outages_text += maintenance_window['mw_name'] + "\n"
                for outage in maintenance_window["mw_outages"]:
                    print outage.keys()
                    outage_type = OutageType.objects.get(slug=outage["outage_type"])
                    
                    outage_template = OutageTemplate.objects.get(outagetemplate_language = notification_language, outagetemplate_outagetype = outage_type)
                    outage_template_text = outage_template.outagetemplate_text
                    outages_text += outage_template_text.replace("%circuit_name%",outage['outage_channel']) + "\n"
                    
                outages_text +="\n"
                
            notification_body = notification_template.notificationtemplate_text
            notification_body = notification_body.replace("%work_number%", work_number)
            notification_body = notification_body.replace("%client_name%", client_name)
            work_location = WorkLocationDescription.objects.get(worklocationlang=notification_language, worklocation = work_obj.work_region.region_location).worklocdesc
            work_region = WorkRegionDescription.objects.get(workregionlang=notification_language, workregion=work_obj.work_region).workregdesc
        
            notification_body = notification_body.replace("%work_location%", work_location)
            notification_body = notification_body.replace("%work_region%",work_region)
            notification_body = notification_body.replace("%work_type%", work_type)
            notification_body = notification_body.replace("%work_start_time%",work_obj.work_start_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M'))
            notification_body = notification_body.replace("%work_end_time%",work_obj.work_end_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M'))
            notification_body = notification_body.replace("%outages_block%", outages_text)
            response = HttpResponse(notification_body)
            
            notification_subject = notification_template.notificationtemplate_subject.replace("%work_number%",work_obj.work_number)
            
            
            notif_json = simplejson.dumps({"subject":notification_subject, "body":notification_body})
            response = HttpResponse(notif_json, content_type='application/json')
            
            return HttpResponse(response)
        return HttpResponse("fuck you")

#@transaction.commit_manually
@csrf_exempt
def load_works(request):
        '''
    Input file parse options and file to parse
    must return json on success/error'''
        if request.method == "POST":
            
            file_parse_option = request.POST[u'FileParseOpts']
            existing_work_action = request.POST[u'ExstWorkOpts']
            
            #===================================================================
            # print existing_work_action
            # 
            # 
            # if file_parse_option == 'CreateWorksOnly':
            #     print 'Creating works'
            # if file_parse_option == 'CreateNotifications':
            #     print 'Create notifications'
            # if file_parse_option == 'CheckErrors':
            #     print 'CheckErrors'
            #===================================================================
                
            input_file = request.FILES['input_file']
            #print 'inputfile len',len(input_file.read())
            
            try:
                #raise RecordParseError("0x0001","blablablabal")
                w = WorkContainer(input_file)
                w.parse(file_parse_option, existing_work_action)
            except RecordParseError as e:
                print e.problem_string
#                transaction.rollback()
                test_error = simplejson.dumps({"error":e.problem_string + " " + e.work_number, "success":False})
                response = HttpResponse(test_error, content_type='application/json')
                return HttpResponse(response)
            #output_file = HttpResponse ( content_type = 'txt/csv')
            #output_file['Content-Disposition'] = 'attachment; filename=output.csv'
#            transaction.commit()
            #options = {""}
            
            #csv_opt = CSVParseOptions()
            #csv_opt.options.update()
            
            #csv_processor = CSVProcessor( input_file, output_file)
            #csv_processor.process_file()
            
            #return output_file
            test_error = simplejson.dumps({"error":[], "success":True})
            response = HttpResponse(test_error, content_type='application/json')
            return HttpResponse(response)
            #return HttpResponseRedirect("/rnr/works/")
        else:
            return HttpResponseRedirect("/rnr/works/")

def rnr_about(request):
    return render_to_response("rnr_about.html")