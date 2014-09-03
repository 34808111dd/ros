

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
#from django.core.servers.basehttp import FileWrapper

#from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from forms import UploadFileForm, NewRecordForm, RecordsForm, ClientForm
from django.template import RequestContext, Context

from models import DictRecord, Client, Contact, Language
from processor.csvfile import CSVProcessor, CSVParseOptions

import json
from django.core import serializers


#    csv_row[time_row_number] = time_string.encode('1251')




def rnr_home(request):
    return HttpResponse('test')



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
    


def clients(request):
    if request.method == "POST":
        cl_form = ClientForm()
        return render_to_response('clients.html',{'cl_form':cl_form}, context_instance=RequestContext(request))
    if request.method == "GET":
        client_objects = Client.objects.all()
        client_list = []
        for client in client_objects:
            contacts = Contact.objects.filter(client=client).values('contact_email', 'slug')
            client.contacts=contacts
            print contacts
            language = Language.objects.filter(client=client).values('language_name','slug')
            client.language = language
            client_list.append(client)
        print dir(client_objects)
        return render_to_response('clients.html',locals(), context_instance=RequestContext(request))
    

def clients_get_all_json( request ):
    #cl_form = ClientForm(request.POST)
    #clients = Client.objects.raw("select rnr_client.id, rnr_client.slug as client_slug, rnr_language.slug as language_slug, rnr_client.client_name, rnr_language.language_name from rnr_client inner join rnr_language on rnr_client.client_language_id = rnr_language.id;")
    client_objs = Client.objects.values('slug', 'client_name', 'client_language__slug','client_language__language_name')  
    
#     c = serializers.serialize('json', clients)
    
    
    #[client_slug:{'name':}]
    clients = []
    for client_obj in client_objs:
        sl = client_obj.pop('slug')
        clients.append({})
        client_data={}
        client_data['client_name']=client_obj.client_name
        client_data['client_language']=client_obj.client_language__language_name
        client_data['language_slug']=client_obj.client_language__slug
        
        clients.append({client_obj.slug:client_data})
#         contact_objs = Contact.objects.filter(client__slug=client_obj.slug).values('slug', 'client__slug')
#         [c for c in contact_objs]
            
    
    print clients
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
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(clients)
    return response