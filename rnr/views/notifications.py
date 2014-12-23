'''
Created on Dec 20, 2014

@author: Coeurl
'''

import simplejson, json
from rnr.models import Notification, NotificationState, Language,\
NotificationStateDescription, NotificationTypeDescription, Client, Work,\
NotificationType, WorkState, NotificationTemplate, WorkTypeDescription,\
WorkLocationDescription, WorkRegionDescription, OutageType, OutageTemplate
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from processor.shortcuts import request_type, lang_aware
from rnr.forms import NotificationForm
from processor.emails import EmailProcessor
from django.db.models import Q
from general import local_tz

@request_type('GET', True)
@lang_aware({'en':'English','ru':'Russian'})
def get_notifications_json(request, lang):
    work_slug = request.GET["work_slug"]
    notifications = Notification.objects.filter(notification_work__slug=work_slug).values("slug", "notification_client__client_name", "notification_type__notificationtype_name", "notification_state__notificationstate_name")
    if "notification_type" in request.GET:
        notification_type = request.GET["notification_type"]
        if notification_type:
            notifications = notifications.filter(notification_type__notificationtype_name = notification_type).values("slug", "notification_client__client_name", "notification_type__notificationtype_name", "notification_state__notificationstate_name")
        
    if "notification_state" in request.GET:
        notification_state = request.GET["notification_state"]
        if notification_state:
            notifications = notifications.filter(notification_state__notificationstate_name = notification_state).values("slug", "notification_client__client_name", "notification_type__notificationtype_name", "notification_state__notificationstate_name")
    l = sorted(list(notifications), reverse=False, key=lambda x: x["notification_client__client_name"])
    
    lang_object = Language.objects.get(language_name=lang)
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
    notifications = simplejson.dumps(l)
    response = HttpResponse(notifications, content_type='application/json')
    return response


@request_type('GET', True)
@lang_aware({'en':'English','ru':'Russian'})
def get_notification_type_all_json(request, lang):
    lang_object = Language.objects.get(language_name=lang)
    notification_types = NotificationTypeDescription.objects.filter(notificationtypelang=lang_object).values("notificationtype__slug","notificationtypedesc")
    response = HttpResponse(simplejson.dumps(list(notification_types)), content_type='application/json')
    return response


#TODO - rework response as json
@csrf_exempt
@request_type('POST', True)
def del_notification(request):
    '''
    delete notification based on slug
    '''
    notification_slug = request.POST["notification_slug"]
    notification_obj = Notification.objects.get(slug=notification_slug)
    notification_obj.delete()
    return HttpResponse("OK")
        

#TODO = rework response as json
@csrf_exempt
@request_type('POST', True)
def add_new_notification( request ):
    new_notification_form = NotificationForm(request.POST)
    if new_notification_form.is_valid():
        
        notification_client = new_notification_form.cleaned_data['notification_client']
        notification_work = new_notification_form.cleaned_data['notification_work']
        notification_template = new_notification_form.cleaned_data['notification_template']
        notification_complete_text = new_notification_form.cleaned_data['notification_complete_text']
        shiny_new_notification = Notification(notification_client=notification_client,\
                                              notification_work=notification_work,\
                                              notification_template = notification_template,\
                                              notification_complete_text = notification_complete_text)
        shiny_new_notification.save()
        return HttpResponse("OK")
    else:
        print new_notification_form.errors.as_text()
        return HttpResponse(new_notification_form.errors.as_text())

#TODO = rework response as json
@csrf_exempt
@request_type('POST', True)
def send_notification(request):
    notification_slug = request.POST["notification_slug"]
    notification_obj = Notification.objects.get(slug=notification_slug)
    e_processor = EmailProcessor()
    print e_processor
    e_processor.add_to_queue(notification_obj)
    e_processor.send_all()
    notif_sent_state = NotificationState.objects.get(notificationstate_name='sent')
    notification_obj.notification_state = notif_sent_state
    notification_obj.save()
    return HttpResponse("OK")


@csrf_exempt
@request_type('POST', True)
def send_all_notifications(request):
    work_slug = request.POST["work_slug"]
    send_notif = True if request.POST["send_notif"] == "true" else False
    send_init_messages = True if request.POST["send_init_messages"] == "true" else False
    send_error_messages = True if request.POST["send_error_messages"] == "true" else False
    send_sent_messages = True if request.POST["send_sent_messages"] == "true" else False
    
    if send_notif:
        q_obj_notif_type = Q(notification_type__notificationtype_name = "notification")
    else:
        q_obj_notif_type = Q(notification_type__notificationtype_name = "cancel")
    
    if send_init_messages:
        q_obj_state_init = Q(notification_state__notificationstate_name = "init")
    else:
        q_obj_state_init = Q()
        
    if send_error_messages:
        q_obj_state_error = Q(notification_state__notificationstate_name = "sent_error")
    else:
        q_obj_state_error = Q()
    
    if send_sent_messages:
        q_obj_state_sent = Q(notification_state__notificationstate_name = "sent")
    else:
        q_obj_state_sent = Q()
        
    lll = Notification.objects.filter(q_obj_notif_type).filter(Q(notification_work__slug = work_slug)).filter(q_obj_state_init | q_obj_state_error | q_obj_state_sent)
    sender = EmailProcessor()
    
    for x in lll:
        print x.slug
        sender.add_to_queue(x)
        
    sender.send_all()
    return HttpResponse(simplejson.dumps({"error":"","success":True, "total_added":lll.count()}), content_type='application/json')

@request_type('GET', True)
def view_notification(request):
    notification_slug = request.GET["notification_slug"]
    notification_obj = Notification.objects.get(slug=notification_slug)
    notification_obj = simplejson.dumps({'notification_complete_text':notification_obj.notification_complete_text,\
                                         'notification_subject':notification_obj.notification_subject})
    response = HttpResponse(notification_obj, content_type='application/json')
    return response

@csrf_exempt
@request_type('POST', True)
def save_notification(request):
    '''
    save notification, MW, outages in base
    '''
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
@request_type('POST', True)
def update_notification(request):
    '''
    Updates body and subject of notification
    '''
    new_subject = request.POST["message_subject"]
    new_body = request.POST["message_body"]
    notification_slug = request.POST["notification_slug"]
    notif_dj_obj = Notification.objects.get(slug=notification_slug)
    notif_dj_obj.notification_subject = new_subject
    notif_dj_obj.notification_complete_text = new_body
    notif_dj_obj.save()
    return HttpResponse("ok")
        
        
        
        
@csrf_exempt
@request_type('POST', True)
def gen_cancel(request):
    work_slug = request.POST["work_slug"]
    work_obj = Work.objects.get(slug=work_slug)
    canceled_work_state = WorkState.objects.get(workstate_name = "Canceled")
    
    if work_obj.work_state.workstate_name != "Canceled":
        notification_type_obj = NotificationType.objects.get(notificationtype_name='cancel')
        clients = Client.objects.filter(notification__notification_work__slug = work_slug)#.filter(~Q(notification__notification_type = notification_type_obj))
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
        work_obj.work_state = canceled_work_state
        work_obj.save()
        return HttpResponse("ok")
    else:
        return HttpResponse("already canceled")

@csrf_exempt
@request_type('POST', True)
def gen_notification(request):
    my_shiny_new_object = json.loads(request.POST["test"])
    print my_shiny_new_object
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
            print 'outage:', outage
            outage_type = OutageType.objects.get(slug=outage["outage_type"])
            
            outage_template = OutageTemplate.objects.get(outagetemplate_language = notification_language, outagetemplate_outagetype = outage_type)
            outage_template_text = outage_template.outagetemplate_text
            print outage_template_text
            outages_text += outage_template_text + '\n---\n' + outage['outage_channel']+'\n' #.replace("%circuit_name%",outage['outage_channel']) + "\n"
            
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


