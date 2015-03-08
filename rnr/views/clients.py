'''
Created on Dec 21, 2014

@author: Coeurl
'''
#===============================================================================
# General imports
#===============================================================================
import simplejson

#===============================================================================
# Django imports
#===============================================================================
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#===============================================================================
# Models imports
#===============================================================================
from rnr.models import Client, Contact

#===============================================================================
# Form imports
#===============================================================================
from rnr.forms import ClientForm, UpdateClientForm

#===============================================================================
# Inner imports
#===============================================================================

from processor.shortcuts import request_type, lang_aware, http400onError
from processor.emails import EmailProcessor
from processor.errors import ClientAlreadyExists, AppError

#tested in rnr.tests.clients.views
@request_type('GET', True)
def clients_get_all_json( request ):
    client_objs = Client.objects.values('slug', 'client_name', 'client_language__slug','client_language__language_name', 'client_display_name')  
    clients = []
    for client_obj in client_objs:
        client_slug = client_obj.pop('slug')
        contact_objs = Contact.objects.filter(client__slug=client_slug).values('slug', 'contact_email')
        client_data={'client_slug':client_slug, 'attribs':client_obj, 'contacts':list(contact_objs)}
        clients.append(client_data)
    clients = sorted(clients, reverse=False, key=lambda x: x["attribs"]["client_name"])
    clients = simplejson.dumps(clients)
    response = HttpResponse(clients, content_type='application/json')
    return response

#tested in rnr.tests.clients.views
@http400onError
@request_type('GET', True)
def get_client_info(request):
    #===========================================================================
    # return json object, consists of name, language slug, client e-mails
    #===========================================================================
    client_slug = request.GET["slug"]
    client_obj = Client.objects.get(slug=client_slug)
    client_contacts = Contact.objects.filter(client=client_obj).values_list('contact_email')
    client_contacts = [x[0] for x in client_contacts]
    client_info_json = simplejson.dumps({'client_name':client_obj.client_name, 'client_language':client_obj.client_language.slug,\
                                        'client_display_name':client_obj.client_display_name,'client_contacts':client_contacts})
    response = HttpResponse(client_info_json, content_type='application/json')
    return response

#tested in rnr.tests.clients.views
@request_type('GET', True)
def get_client_names_json(request):
    clients = Client.objects.all().values('slug','client_name')
    clients = simplejson.dumps(list(clients))
    response = HttpResponse(clients, content_type='application/json')
    return response

#tested in rnr.tests.clients.views
@csrf_exempt
@request_type('POST', True)
@lang_aware({'en':'English','ru':'Russian'})
def add_new_client(request, lang):
    '''
    add new client
    '''
    new_client_form = ClientForm(request.POST)
    try:
        if new_client_form.is_valid():
            client_name = new_client_form.cleaned_data['client_name']
            client_display_name = new_client_form.cleaned_data['client_display_name']
            client_language = new_client_form.cleaned_data['client_language']
            client_contacts = new_client_form.cleaned_data['client_emails']
            shiny_new_client = Client(client_name = client_name,client_display_name = client_display_name,client_language=client_language)
            shiny_new_client.save()
            for contact in client_contacts:
                new_contact = Contact(client=shiny_new_client, contact_email=contact)
                new_contact.save()
            return HttpResponse('{"errors": [], "success": true}',content_type='application/json')
        else:
            errors = {}
            for error in new_client_form.errors.items():
                errors[error[0]] = error[1]
            return HttpResponse(simplejson.dumps({"errors": errors, "success": False}) ,content_type='application/json')
    except ClientAlreadyExists as e:
        try:
            raise AppError(e.type_id, language=lang, error_string=e.error_string)
        except AppError as app_error:
            return HttpResponse(simplejson.dumps({"errors": {'client_name':app_error.app_error_desc_obj.apperror_desc_desc+e.error_string}, "success": False}) ,content_type='application/json')

#tested in rnr.tests.clients.views
@csrf_exempt
@request_type('POST', True)
@lang_aware({'en':'English','ru':'Russian'})
@http400onError
def update_client_info(request, lang):
    client_slug = request.POST["slug"]
    client_obj = Client.objects.get(slug=client_slug)
    cl_upd_form = UpdateClientForm(request.POST)
    if cl_upd_form.is_valid():
        #client_obj.update(display_name = cl_upd_form.cleaned_data['client_update_display_name'], client_language=cl_upd_form.cleaned_data['client_update_language'])
        client_obj.client_display_name = cl_upd_form.cleaned_data['client_update_display_name']
        client_obj.client_language = cl_upd_form.cleaned_data['client_update_language']
        client_obj.save()
        Contact.objects.filter(client = client_obj).delete()
        for contact in cl_upd_form.cleaned_data['client_update_emails']:
            cont_obj = Contact(client = client_obj, contact_email = contact)
            cont_obj.save()
        return HttpResponse('{"errors": [], "success": true}',content_type='application/json')
    else:
        errors = {}
        for error in cl_upd_form.errors.items():
            errors[error[0]]=error[1]
        return HttpResponse(simplejson.dumps({"errors": errors, "success": False}) ,content_type='application/json')

#TODO replace answer with json answer
#tested in rnr.tests.clients.views
@csrf_exempt
@request_type('POST', True)
@http400onError
def del_client(request):
    '''
    remove client, remove all contacts, remove notifications.
    '''
    client_slug = request.POST['client_slug']
    client_obj = Client.objects.get(slug = client_slug)
    client_obj.delete()
    return HttpResponse("OK")

#TODO replace answer with json answer
#tested in rnr.tests.clients.views
@csrf_exempt
@request_type('POST', True)
@http400onError
def del_contact(request):
    '''
    remove contact
    '''
    contact_slug = request.POST['contact_slug']
    contact_obj = Contact.objects.get(slug = contact_slug)
    contact_obj.delete()
    return HttpResponse("OK")

