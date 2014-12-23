'''
Created on Dec 19, 2014

@author: Coeurl
'''

from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect, HttpResponse

from processor.shortcuts import request_type
from processor.csvfile import CSVProcessor, CSVParseOptions

from rnr.forms import UploadFileForm, RecordsForm, NewRecordForm
from rnr.models import DictRecord
from django.shortcuts import render_to_response


#===============================================================================
# Old requests, used in old csv parser (processor.csv_file)
#===============================================================================

@request_type('GET',False)
def csv_parser (request):
    '''
    /rnr/csv_parser/
    '''
    def_options = CSVParseOptions()
    upload_file_form = UploadFileForm(def_options.options)
    all_records_form = RecordsForm()
    new_record_form = NewRecordForm()
    dictrecords = DictRecord.objects.all()
    return render_to_response('csv_processor.html', {'all_records_form':all_records_form,\
                              'upload_file_form':upload_file_form,\
                              'new_record_form':new_record_form,\
                              'dictrecords':dictrecords },\
                              context_instance=RequestContext(request))

@request_type('POST',False)
def csv_process(request):
    '''
    /rnr/csv_process/
    POST request to parse uploaded csv file
    '''
    upload_file_form = UploadFileForm(request.POST, request.FILES)
    if upload_file_form.is_valid():
        input_file = upload_file_form.cleaned_data['input_file']
        output_file = HttpResponse ( content_type = 'txt/csv')
        output_file['Content-Disposition'] = 'attachment; filename=output.csv'
        csv_opt = CSVParseOptions()
        csv_opt.options.update(upload_file_form.cleaned_data)
        csv_processor = CSVProcessor( input_file, output_file, csv_opt )
        csv_processor.process_file()
        return output_file
    else:
        return HttpResponseRedirect("/rnr/csv_parser/")

@request_type('POST',False)
def add_new_record( request ):
    '''
    /rnr/add_new_record/
    Used to add records to DictRecord
    '''
    new_record_form = NewRecordForm(request.POST)
    if new_record_form.is_valid():
        init_word  = new_record_form.cleaned_data['init_word']
        replace_word = new_record_form.cleaned_data['replace_word']
        new_record = DictRecord(init_word = init_word, replace_word=replace_word)
        new_record.save()
        return HttpResponseRedirect("/rnr/csv_parser/")
    else:
        return HttpResponseRedirect('/rnr/csv_parser/')

@request_type('POST',False)
def delete_record( request ):
    '''
    /rnr/del_record/
    Delete record from DictRecord
    '''
    del_record_form = RecordsForm(request.POST)
    if del_record_form.is_valid():
        del_list = del_record_form.cleaned_data['Records']
        for x in del_list:
            _tmp_obj = DictRecord.objects.get(init_word = x).delete()
        return HttpResponseRedirect("/rnr/csv_parser/")
    else:
        return HttpResponseRedirect("/rnr/csv_parser/")