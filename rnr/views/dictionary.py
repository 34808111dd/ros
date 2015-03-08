'''
Created on Jan 8, 2015

@author: Coeurl
'''

from processor.shortcuts import request_type, lang_aware, success_response, unsuccess_response
from django.shortcuts import HttpResponseRedirect, HttpResponse
from rnr.models import DictRecord
from rnr.forms import RnrDictRecordForm
from django.views.decorators.csrf import csrf_exempt


import simplejson

@csrf_exempt
@request_type('POST',True)
@lang_aware({'en':'English','ru':'Russian'})
def add_dict_record (request, lang):
    '''
    /rnr/csv_parser/
    '''
    print 'view lang:', lang
    init_word = request.POST["init_word"]
    replace_word = request.POST["replace_word"]
    data = {'init_word':init_word, 'replace_word':replace_word, 'lang':lang}
    new_record_form = RnrDictRecordForm(data)
    if new_record_form.is_valid():
        new_record_obj = DictRecord(init_word=init_word, replace_word=replace_word)
        new_record_obj.save()
        return HttpResponse(success_response, content_type='application/json')
    else:
        errors = {}
        for error in new_record_form.errors.items():
            errors[error[0]]=error[1]
        return HttpResponse(simplejson.dumps({"errors": errors, "success": False}) ,content_type='application/json')

@csrf_exempt
@request_type('POST', True)
def del_dict_record(request):
    '''
    delete dict record
    '''
    slug = request.POST['slug']
    try:
        del_word = DictRecord.objects.get(slug=slug)
        del_word.delete()
        print 'deleted'
        return HttpResponse(success_response, content_type='application/json')
    except:
        HttpResponse(unsuccess_response, content_type='application/json')


def get_dict_records(request):
    '''
    all dictionary records, used in responsive table as data source
    '''
    all_records = simplejson.dumps(list(DictRecord.objects.values('slug','init_word', 'replace_word')))
    return HttpResponse(all_records, content_type='application/json')






if __name__ == '__main__':
    pass