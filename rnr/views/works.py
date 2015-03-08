'''
Created on Dec 19, 2014

@author: Coeurl
'''

from processor.shortcuts import request_type, lang_aware, http400onError
from processor.errors import AppError, WorkAlreadyExists,\
WorkEndTimeLessThenStart, FileParseError, TimeParseError,\
UnknownWorkConditionError, UnknownClient, BlankWorkNumber

from processor.tmp_csv_proc import WorkContainer
#from rnr.models import WorkType
from django.shortcuts import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rnr.models import Work, Language, WorkTypeDescription,\
WorkRegionDescription, Notification, Region
from general import local_tz, utc_tz
from rnr.forms import WorkForm
import simplejson
import datetime



#===============================================================================
# Work views
#===============================================================================

#tested in rnr.tests.works.views.test_get_works_json
@request_type('GET', True)
@lang_aware({'en':'English', 'ru':'Russian'})
@http400onError
def get_works_json(request, lang):
    '''
    /rnr/get_works_json
    Get works as json, based on filters
    '''
    work_filter_number = request.GET["work_filter_number"]
    work_filter_pending = request.GET["work_filter_pending"]
    work_filter_upcoming = request.GET["work_filter_upcoming"]
    work_filter_completed = request.GET["work_filter_completed"]
    work_filter_from = request.GET["work_filter_from"]
    work_filter_to = request.GET["work_filter_to"]
    
    work_filter_dict = {"work_filter_number":work_filter_number,\
                      "work_filter_to":work_filter_to,\
                      "work_filter_from":work_filter_from,\
                      "work_filter_pending":work_filter_pending,\
                      "work_filter_upcoming":work_filter_upcoming,
                      "work_filter_completed":work_filter_completed}
    query_time = timezone.now()
    
    #if checked pending filter
    q_obj_p = Q(work_start_date__lte = query_time) &\
              Q(work_end_date__gt = query_time)\
              if work_filter_pending == "true" else Q()
    
    #if checked upcoming filter
    q_obj_u = Q(work_start_date__gt = query_time)\
              if work_filter_upcoming == "true" else Q()
    
    #if checked completed filter
    q_obj_c = Q(work_end_date__lt = query_time)\
              if work_filter_completed == "true" else Q()
    
    #if work number in filter
    q_obj_df = Q(work_number__icontains = work_filter_number)\
               if work_filter_number else Q()
    
    #if work date filter from
    if work_filter_from:
        work_from_date = datetime.date(*[int(x) for x in work_filter_from.split("-")])
        q_obj_ff = Q(work_start_date__gte = work_from_date)
    else:
        q_obj_ff = Q()
    
    #if work date filter to
    if work_filter_to:
        work_to_date = datetime.date(*[int(x) for x in work_filter_to.split("-")])
        q_obj_ft = Q(work_start_date__lte = work_to_date)
    else:
        q_obj_ft = Q()

    work_objects = Work.objects.filter(q_obj_p | q_obj_u | q_obj_c).filter(q_obj_df).filter(q_obj_ff).filter(q_obj_ft)
    list_works=[]
    
    for work in work_objects:
        dict_work={}
        dict_work["slug"] = work.slug
        dict_work["work_number"] = work.work_number
        lang_obj = Language.objects.get(language_name=lang)
        dict_work["work_type"] = WorkTypeDescription.objects.get(worktype=work.work_type, worktypelang=lang_obj).worktypedesc
        dict_work["work_region"] = WorkRegionDescription.objects.get(workregionlang = lang_obj, workregion=work.work_region).workregdesc
        dict_work["work_created_date"] = work.work_added.astimezone(local_tz).strftime('%d.%m.%Y %H:%M')
        
        q_obj_filter_by_work = Q(notification_work__slug=work.slug)
        q_obj_notif_type_n = Q(notification_type__notificationtype_name="notification")
        q_obj_notif_type_c = Q(notification_type__notificationtype_name="cancel")
        q_obj_notif_state_init = Q(notification_state__notificationstate_name="init")
        q_obj_notif_state_sent = Q(notification_state__notificationstate_name="sent")
        q_obj_notif_state_sent_err = Q(notification_state__notificationstate_name="sent_error")
        q_obj_notif_state_init = Q(notification_state__notificationstate_name="init")
        
        #notifications = Notification.objects.filter(notification_work__slug=work.slug)
        init_notifications = Notification.objects.filter(q_obj_filter_by_work &\
                                                         q_obj_notif_state_init&\
                                                         q_obj_notif_type_n).count()

        sent_notifications = Notification.objects.filter(q_obj_filter_by_work &\
                                                         q_obj_notif_state_sent&\
                                                         q_obj_notif_type_n).count()
        sent_error_notifications = Notification.objects.filter(q_obj_filter_by_work &\
                                                         q_obj_notif_state_sent_err&\
                                                         q_obj_notif_type_n).count()
                                                         
        init_cancel_notifications = Notification.objects.filter(q_obj_filter_by_work &\
                                                                q_obj_notif_state_init &\
                                                                q_obj_notif_type_c).count()
                                                                
        sent_cancel_notifications = Notification.objects.filter(q_obj_filter_by_work,\
                                                                q_obj_notif_state_sent,\
                                                                q_obj_notif_type_c).count()
                                                                
        sent_error_cancel_notifications = Notification.objects.filter(q_obj_filter_by_work,\
                                                                      q_obj_notif_state_sent_err,\
                                                                      q_obj_notif_type_c).count()
        dict_work["init_notifications"] = init_notifications
        dict_work["sent_notifications"] = sent_notifications
        dict_work["sent_error_notifications"] = sent_error_notifications
        dict_work["init_cancel_notifications"] = init_cancel_notifications
        dict_work["sent_cancel_notifications"] = sent_cancel_notifications
        dict_work["sent_error_cancel_notifications"] = sent_error_cancel_notifications
        
        if work.work_state.workstate_name != "Canceled":#WorkTypes.objects.get(
            if work.work_start_date.astimezone(local_tz) > timezone.now() < work.work_end_date.astimezone(local_tz):
                dict_work["work_state"] = "Upcoming"
            if work.work_start_date.astimezone(local_tz) <= timezone.now() <= work.work_end_date.astimezone(local_tz):
                dict_work["work_state"] = "Pending"
            if work.work_start_date.astimezone(local_tz) < timezone.now() > work.work_end_date.astimezone(local_tz):
                dict_work["work_state"] = "Completed"
        else:
            dict_work["work_state"] = "Canceled"
        
        dict_work["work_start_date"] = work.work_start_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M')
        dict_work["work_end_date"] = work.work_end_date.astimezone(local_tz).strftime('%d.%m.%Y %H:%M')
        list_works.append(dict_work)
#TODO - fix the bug with sort by date (sorting based on day number only)
    list_works = sorted(list_works, reverse=True, key=lambda x: x["work_created_date"])
    works = simplejson.dumps(list_works)
    response = HttpResponse(works, content_type='application/json')
    response.set_cookie(key="filter_works", value=simplejson.dumps(work_filter_dict), max_age=365*24*60*60, expires=None, path='/')
    return response

#tested in rnr.tests.works.views.test_get_work_name_json
@request_type('GET', True)
@http400onError
def get_work_name_json(request):
    '''
    used in notification page
    '''
    work_slug = request.GET["slug"]
    work = Work.objects.values('work_number').get(slug=work_slug)
    response = HttpResponse(simplejson.dumps(work), content_type='application/json')
    return response

#tested in rnr.tests.works.views.get_work_slug
@request_type('GET', True)
@http400onError
def get_work_slug(request):
    '''
    used in notification page to allow filter by work_number
    '''
    work_number = request.GET["work_number"]
    work = Work.objects.values("slug").get(work_number=work_number)
    response = HttpResponse(simplejson.dumps(work), content_type='application/json')
    return response

#tested in rnr.tests.works.views.test_get_work_numbers_json
@request_type('GET', True)
def get_work_numbers_json(request):
    '''
    used in autocomplete work_number
    '''
    works = Work.objects.values('slug','work_number')
    works = simplejson.dumps([_x for _x in works])
    response = HttpResponse(works, content_type='application/json')
    return response


#tested in rnr.tests.works.views.test_get_works_total_count
@request_type('GET', True)
def get_works_total_count(request):
    '''
    used to display work count
    '''
    work_count = Work.objects.count()
    response = HttpResponse(simplejson.dumps({"work_count":work_count}), content_type='application/json')
    return response

#tested in rnr.tests.works.views.test_get_worktypes_all_json
@request_type('GET', True)
@lang_aware({'en':'English','ru':'Russian'})
def get_worktypes_all_json(request, lang):
    '''used on work page'''
    lang_object = Language.objects.get(language_name=lang)
    work_types = WorkTypeDescription.objects.filter(worktypelang=lang_object).values('worktype__slug', 'worktypedesc')
    response = HttpResponse(simplejson.dumps(list(work_types)), content_type='application/json')
    return response


#tested in rnr.tests.works.views.test_add_new_work
@csrf_exempt
@request_type('POST', True)
@lang_aware({'en':'English','ru':'Russian'})
def add_new_work( request, lang):
    new_work_form = WorkForm(request.POST)
    
    normal_response = {"error":"", "success":True}
    
    try:
        if new_work_form.is_valid():
            work_number = new_work_form.cleaned_data['work_number']
            work_type = new_work_form.cleaned_data['work_type']
            work_start_datetime = new_work_form.cleaned_data['work_start_datetime']
            work_end_datetime = new_work_form.cleaned_data['work_end_datetime']
            work_region = Region.objects.get(slug=new_work_form.cleaned_data['work_region'])
            
            work_start_datetime = work_start_datetime.astimezone(utc_tz)
            work_end_datetime = work_end_datetime.astimezone(utc_tz)
            
            work_added = timezone.now()
            
            shiny_new_work = Work(work_number=work_number, work_type=work_type, \
                                  work_start_date = work_start_datetime,\
                                  work_end_date = work_end_datetime, work_region = work_region, work_added=work_added)
            shiny_new_work.save()
            return HttpResponse(simplejson.dumps(normal_response) ,content_type='application/json')
        else:
            errors = {}
            for error in new_work_form.errors.items():
                errors[error[0]] = error[1]
            return HttpResponse(simplejson.dumps({"errors": errors, "success": False}) ,content_type='application/json')
    except WorkAlreadyExists as e:
        print e.error_string
    
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as e:
            print e.error_in_json
            
    except WorkEndTimeLessThenStart as e:
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as e:
            print e.error_in_json
    
    response = HttpResponse(e.error_in_json, content_type='application/json')
    return response


#tested in rnr.tests.works.views.test_delete_work
@csrf_exempt
@request_type('POST', True)
@http400onError
def delete_work(request):
    work_slug = request.POST["work_slug"]
    work_django_obj = Work.objects.get(slug=work_slug)
    work_django_obj.delete()
    return HttpResponse(simplejson.dumps({"success":True}))


#@transaction.commit_manually

#parsing tested in in rnr.tests.parsers.csv_parser
@csrf_exempt
@request_type('POST', True)
@lang_aware({'en':'English','ru':'Russian'})
def load_works(request, lang):
    '''
    Input file parse options and file to parse
    must return json on success/error'''
    file_parse_option = request.POST[u'FileParseOpts']
    existing_work_action = request.POST[u'ExstWorkOpts']
    
    try:
        try:
            input_file = request.FILES['input_file']
        except:
            raise FileParseError('')
        w = WorkContainer(input_file)
        w.parse(file_parse_option, existing_work_action)
        
    except FileParseError as e:
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as e:
            response = HttpResponse(e.error_in_json, content_type='application/json')
            return HttpResponse(response)
    except TimeParseError as e:
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as e:
            response = HttpResponse(e.error_in_json, content_type='application/json')
            return HttpResponse(response)
    except UnknownWorkConditionError as e:
        print e.error_string
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as e:
            response = HttpResponse(e.error_in_json, content_type='application/json')
            return HttpResponse(response)
    except UnknownClient as e:
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as e:
            response = HttpResponse(e.error_in_json, content_type='application/json')
            return HttpResponse(response)
    except BlankWorkNumber as e:
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as e:
            response = HttpResponse(e.error_in_json, content_type='application/json')
            return HttpResponse(response)
#                transaction.rollback()
    test_error = simplejson.dumps({"error":[], "success":True})
    response = HttpResponse(test_error, content_type='application/json')
    return HttpResponse(response)

