'''
Created on Dec 10, 2014

@author: Coeurl
'''
import unittest
from django.test import Client
from django.core.urlresolvers import reverse
import simplejson
from django.test import TestCase
from unittest import skip

@skip
class Test_client(TestCase):
#===============================================================================
# tests work add view
#===============================================================================

    def setUp(self):
        self.kargs = {
        'slug':'Eb37aCc9D5F2'
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
    
    def test_client_info(self):
        cl = Client()
        url = reverse('rnr.views_old.get_client_info')
        resp = cl.get(url, self.kargs)
        #print resp


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()