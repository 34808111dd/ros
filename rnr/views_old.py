import json
import simplejson
import datetime

from django.http import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from django.db import transaction
from django.db.models import Q

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


from django.core.exceptions import ValidationError

from forms import UploadFileForm, NewRecordForm, RecordsForm, ClientForm, WorkForm, NotificationForm, UpdateClientForm

from models import DictRecord, Client, Contact, Language, WorkType, Work, \
    NotificationTemplate, Notification, Outage, OutageType, Location, Region, \
    MaintenanceWindow, OutageTemplate, NotificationType, NotificationState, WorkTypeDescription,\
    WorkLocationDescription, WorkRegionDescription, NotificationTypeDescription, OutageTypeDescription,\
    NotificationStateDescription, WorkState


from processor.emails import EmailProcessor
from processor.tmp_csv_proc import WorkContainer
from processor.errors import FileParseError, AppError, TimeParseError, UnknownWorkConditionError,\
    BlankWorkNumber, UnknownClient, WorkAlreadyExists, WorkEndTimeLessThenStart, ClientAlreadyExists
from processor.shortcuts import request_type, lang_aware

local_tz = timezone.get_current_timezone()
utc_tz = timezone.utc




@request_type('GET', True)
def get_message_queue_len(request):
    _x = EmailProcessor()
    print "get_message_queue", _x, len(_x.notifications_queue)
    response = HttpResponse(simplejson.dumps({"message_queue_len":len(_x.notifications_queue)}))
    return response







def get_languages_all_json(request):
    if request.method == "GET":
        languages = Language.objects.values('slug','language_name')
        languages = simplejson.dumps(list(languages))
        response = HttpResponse(languages, content_type='application/json')
        return response




#def get_client_names_json(request):
#    if request.method == 'GET':
#        clients = Client.objects.all().values_list('client_name', flat=True)
#        clients = simplejson.dumps(list(clients))
#        print clients
#        response = HttpResponse(clients, content_type='application/json')
#        return response
    
    
    

    
@csrf_exempt
def reset_message_queue(request):
    if request.method == 'POST':
        _x = EmailProcessor()
        _x._reset_queue = True
        return HttpResponse("blah")

    
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




@request_type('GET', False)
def data(request):
    records = DictRecord.objects.all().values_list('init_word', 'replace_word')
    l = []
    for rec in records:
        l.append({'init_word':rec[0],'replace_word':rec[1]})
    l=sorted(l, key=lambda x: x['init_word'])
    return StreamingHttpResponse(json.dumps(l), content_type='application/json')
        
    
def tmp_req(request):
    if request.method == 'POST':
        #if request.is_ajax():
            #print 'Ajax request'
        print 'posted:', request.POST
        l=request.POST.get("work_number","blah")
        return HttpResponse(simplejson.dumps({'data':l}), content_type='application/json')
        
