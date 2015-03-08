'''
Created on Dec 22, 2014

@author: Coeurl
'''
import unittest
from django.test import Client
#from django.core.exceptions import ObjectDoesNotExist
from rnr.models import Work, WorkType, WorkTypeDescription, Region
import simplejson
import Cookie


class TestWorkViews(unittest.TestCase):


    def test_get_work_name_json(self):
        #=======================================================================
        # Good request, get/json
        #=======================================================================
        cl = Client()
        existing_work = Work.objects.get(id=1)
        response = cl.get('/rnr/get_work_name_json', data={'slug':existing_work.slug},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.content, simplejson.dumps({'work_number':existing_work.work_number}))
        #=======================================================================
        # Bad request, post/json, should return Http400
        #=======================================================================
        response = cl.get('/rnr/get_work_name_json', data={'slug':existing_work.slug},\
                           content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = cl.post('/rnr/get_work_name_json', data={'slug':existing_work.slug},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
        response = cl.get('/rnr/get_work_name_json', data={'slug':'some_random_string'},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        
        response = cl.get('/rnr/get_work_name_json', data={'blah':'some_random_string'},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
    def test_get_work_slug(self):
        cl = Client()
        existing_work = Work.objects.get(id=1)
        #=======================================================================
        # Good request
        #=======================================================================
        response = cl.get('/rnr/get_work_slug', data={'work_number':existing_work.work_number},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.content, simplejson.dumps({'slug':existing_work.slug}))
        #=======================================================================
        # Bad request, post/json, should return Http400
        #=======================================================================
        response = cl.get('/rnr/get_work_slug', data={'work_number':existing_work.work_number},\
                           content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = cl.post('/rnr/get_work_slug', data={'work_number':existing_work.work_number},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        response = cl.get('/rnr/get_work_slug', data={'work_number':'some_random_string'},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        response = cl.get('/rnr/get_work_slug', data={'blah':'some_random_string'},\
                           content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
        
    def test_get_work_numbers_json(self):
        cl = Client()
        #=======================================================================
        # Good request
        #=======================================================================
        response = cl.get('/rnr/get_work_numbers_json', content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(len(simplejson.loads(response.content)), Work.objects.count())
        #=======================================================================
        # Bad request, post/json, should return Http400
        #=======================================================================
        response = cl.post('/rnr/get_work_numbers_json', content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        response = cl.post('/rnr/get_work_numbers_json', data={'blah':'blah'})
        self.assertEqual(response.status_code, 400)
        
        
    def test_get_works_total_count(self):
        cl = Client()
        #=======================================================================
        # Good requests
        #=======================================================================
        response = cl.get('/rnr/get_works_total_count', content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.content, simplejson.dumps({'work_count':Work.objects.count()}))
        #=======================================================================
        # Bad request, post/json, should return Http400
        #=======================================================================
        response = cl.post('/rnr/get_works_total_count', content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        response = cl.get('/rnr/get_works_total_count')
        self.assertEqual(response.status_code, 400)
        
    def test_get_worktypes_all_json(self):
        cl = Client()
        #=======================================================================
        # Good requests
        #=======================================================================
        cl.cookies = Cookie.SimpleCookie()
        cl.cookies["lang"]="en"
        response = cl.get('/rnr/get_worktypes_all_json', content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        wt_objects = WorkTypeDescription.objects.filter(worktypelang__language_name='English').values('worktype__slug','worktypedesc')
        self.assertEqual(response.content, simplejson.dumps(list(wt_objects)))
        #=======================================================================
        # Bad request, post/json, should return Http400
        #=======================================================================
        response = cl.post('/rnr/get_worktypes_all_json', content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        response = cl.get('/rnr/get_worktypes_all_json')
        self.assertEqual(response.status_code, 400)
        
    def test_add_new_work(self):
        cl = Client()
        #=======================================================================
        # Good requests
        #=======================================================================
        wt = WorkType.objects.get(id=1)
        wr = Region.objects.get(id=1)
        data = {'work_number':'12345', 'work_start_datetime':'12/12/2014 15:00',\
                'work_end_datetime':'12/12/2014 16:00', 'work_type':wt.slug, 'work_region':wr.slug}
        response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(simplejson.dumps({'error':'','success':True}), response.content)
        #=======================================================================
        # Bad requests
        #=======================================================================
        #No work_number
        data = {'work_number':'', 'work_start_datetime':'12/12/2014 15:00',\
                'work_end_datetime':'12/12/2014 16:00', 'work_type':wt.slug, 'work_region':wr.slug}
        response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(simplejson.dumps({"errors": {"work_number": ["This field is required."]}, "success": False}), response.content)
        #No start date
        data = {'work_number':'123456', 'work_start_datetime':'',\
                'work_end_datetime':'12/12/2014 16:00', 'work_type':wt.slug, 'work_region':wr.slug}
        response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(simplejson.dumps({"errors": {"work_start_datetime": ["This field is required."]}, "success": False}), response.content)
        #No end date
        data = {'work_number':'1234567', 'work_start_datetime':'12/12/2014 15:00',\
                'work_end_datetime':'', 'work_type':wt.slug, 'work_region':wr.slug}
        response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(simplejson.dumps({"errors": {"work_end_datetime": ["This field is required."]}, "success": False}), response.content)
        #No work type
        data = {'work_number':'123415', 'work_start_datetime':'12/12/2014 15:00',\
                'work_end_datetime':'12/12/2014 16:00', 'work_type':'blah', 'work_region':wr.slug}
        response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(simplejson.dumps({"errors": {"work_type": ["Select a valid choice. That choice is not one of the available choices."]}, "success": False}), response.content)
        #No work region
        #data = {'work_number':'123w45', 'work_start_datetime':'12/12/2014 15:00',\
        #        'work_end_datetime':'12/12/2014 16:00', 'work_type':wt.slug, 'work_region':'blah'}
        #response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        #print response.content
        #self.assertEqual(simplejson.dumps({"errors": {"work_region": ["Select a valid choice. That choice is not one of the available choices."]}, "success": False}), response.content)
        
    def test_get_works_json(self):
        #=======================================================================
        # Good requests, select one work
        #=======================================================================
        cl = Client()
        cl.cookies = Cookie.SimpleCookie()
        cl.cookies["lang"]='en'
        data = {'work_filter_number':'1401216',
                'work_filter_pending':'false',
                'work_filter_upcoming':'false',
                'work_filter_completed':'true',
                'work_filter_from':'',
                'work_filter_to':''
                }
        response = cl.get('/rnr/get_works_json', data=data, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_list = simplejson.loads(response.content)
        #check if one work returned and slug = faeD1C2Cf3Dd
        self.assertEqual(1, len(result_list))
        self.assertEqual('faeD1C2Cf3Dd', result_list[0]["slug"])
        
        #add upcoming work and filter upcoming
        wt = WorkType.objects.get(id=1)
        wr = Region.objects.get(id=1)
        data = {'work_number':'test_upcoming', 'work_start_datetime':'12/12/2019 15:00',\
                'work_end_datetime':'12/12/2019 16:00', 'work_type':wt.slug, 'work_region':wr.slug}
        response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        data = {'work_filter_number':'',
                'work_filter_pending':'false',
                'work_filter_upcoming':'true',
                'work_filter_completed':'false',
                'work_filter_from':'',
                'work_filter_to':''
                }
        response = cl.get('/rnr/get_works_json', data=data, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_list = simplejson.loads(response.content)
        
        self.assertEqual(1, len(result_list))
        self.assertEqual('test_upcoming', result_list[0]["work_number"])
        
        #add pending work and test filter
        data = {'work_number':'test_pending', 'work_start_datetime':'12/12/2014 15:00',\
                'work_end_datetime':'12/12/2015 16:00', 'work_type':wt.slug, 'work_region':wr.slug}
        response = cl.post('/rnr/add_new_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        data = {'work_filter_number':'',
                'work_filter_pending':'true',
                'work_filter_upcoming':'false',
                'work_filter_completed':'false',
                'work_filter_from':'',
                'work_filter_to':''
                }
        response = cl.get('/rnr/get_works_json', data=data, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_list = simplejson.loads(response.content)
        self.assertEqual(1, len(result_list))
        self.assertEqual('test_pending', result_list[0]["work_number"])
        
        #check with work_filter_from
        data = {'work_filter_number':'',
                'work_filter_pending':'true',
                'work_filter_upcoming':'true',
                'work_filter_completed':'false',
                'work_filter_from':'2015-12-12',
                'work_filter_to':''
                }
        response = cl.get('/rnr/get_works_json', data=data, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_list = simplejson.loads(response.content)
        self.assertEqual(1, len(result_list))
        self.assertEqual('test_upcoming', result_list[0]["work_number"])
        
        #check with both filter set
        data = {'work_filter_number':'',
                'work_filter_pending':'true',
                'work_filter_upcoming':'true',
                'work_filter_completed':'false',
                'work_filter_from':'2014-12-11',
                'work_filter_to':'2015-12-13'
                }
        response = cl.get('/rnr/get_works_json', data=data, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_list = simplejson.loads(response.content)
        self.assertEqual(1, len(result_list))
        self.assertEqual('test_pending', result_list[0]["work_number"])
        #=======================================================================
        # Bad requests should return Http400
        #=======================================================================
        data = {'work_filter_number':'',
                'work_filter_upcoming':'true',
                'work_filter_completed':'false',
                'work_filter_from':'2014-12-11',
                'work_filter_to':'2015-12-13'
                }
        response = cl.get('/rnr/get_works_json', data=data, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
        response = cl.post('/rnr/get_works_json', content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
        response = cl.post('/rnr/get_works_json')
        self.assertEqual(response.status_code, 400)
        
        response = cl.get('/rnr/get_works_json')
        self.assertEqual(response.status_code, 400)
        
    def test_delete_work(self):
        #=======================================================================
        # Good request
        #=======================================================================
        cl = Client()
        w_obj = Work.objects.get(id=10)
        data = {'work_slug':w_obj.slug}
        response = cl.post('/rnr/delete_work', data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.content, simplejson.dumps({'success':True}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Work.objects.filter(id=10)), 0)
        #=======================================================================
        # Bad requests should return Http400
        #=======================================================================
        response = cl.post('/rnr/delete_work', data={'blah':'blah'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        response = cl.get('/rnr/delete_work', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testWorkView']
    unittest.main()