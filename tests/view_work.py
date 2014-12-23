'''
Created on Dec 10, 2014

@author: Coeurl

Used to test work object and json repl
'''
import unittest
from django.test import Client
from django.core.urlresolvers import reverse
import simplejson
from django.test import TestCase
from unittest import skip

@skip
class Test_add_new_work(TestCase):
#===============================================================================
# tests work add view
#===============================================================================

    def setUp(self):
        self.kargs = {
        'ajax':'true',
        'work_end_datetime':'12/00/2014 01:30',
        'work_number':'11882',
        'work_region':'014B402Fe986',
        'work_start_datetime':'12/01/2014 00:00',
        'work_type':'fdBBfbb4BFAc',
                 }
        self.headers = {
        'Host': '127.0.0.1:8000',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://127.0.0.1:8000/rnr/works/',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
                        }


    def tearDown(self):
        pass

    @skip
    def testName(self):
        cl = Client()
        url = reverse('rnr.views_old.add_new_work')
        #print 'creating work'#, simplejson.dumps(self.kargs)
        print 'posting', url, self.kargs
        print 'response:', cl.post(url, data=self.kargs, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print 'request',cl.request()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()