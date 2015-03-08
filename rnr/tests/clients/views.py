'''
Created on Jan 7, 2015

@author: Coeurl
'''
import unittest
import simplejson
from processor.shortcuts import http_request, success_response
from rnr.models import Client, Language, Contact

class TestClientViews(unittest.TestCase):

    def test_clients_get_all_json(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/clients_all'
        response = http_request(url, method='get', content_type=None)
        self.assertEqual(response.status_code, 200)
        result_list = simplejson.loads(response.content)
        target_response = {'attribs': {'client_language__language_name': 'English', 'client_display_name': 'Linx', 'client_language__slug': '9Fb2cfd4f1Eb', 'client_name': 'LINX'}, 'client_slug': '6aCdACBB0233', 'contacts': [{'contact_email': 'mo@linx.net', 'slug': '0a2cf1f426aD'}, {'contact_email': 'Kaznacheev@RT.RU', 'slug': 'e3f33D02dDaF'}]}
        self.assertEqual(result_list[30], target_response)
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method='post', content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', ajax=False)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', ajax=False, content_type=None)
        self.assertEqual(response.status_code, 400)
        
    def test_get_client_info(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/get_client_info'
        cl_obj = Client.objects.get(id=10)
        data = {'slug':cl_obj.slug}
        response = http_request(url, method='get', data=data)
        target_response = {"client_contacts": ["munguu@utnm.mn", "tsbaterdene@utnm.mn", "batsaikhan@gemnet.mn", "Techsupport@gemnet.mn", "khurelbaatar@gemnet.mn"], "client_language": "9Fb2cfd4f1Eb", "client_name": "Gemnet", "client_display_name": "Gemnet"}
        self.assertEqual(simplejson.loads(response.content), target_response)
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method='post', content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', data={'blah':'blah'})
        self.assertEqual(response.status_code, 400)
        
    def test_get_client_names_json(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/get_client_names_json'
        response = http_request(url, method='get', content_type=None)
        self.assertEqual(len(simplejson.loads(response.content)), Client.objects.count())
        #=======================================================================
        # Bad request
        #=======================================================================
        response = http_request(url, method='post', content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', ajax=False)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', data={'blah':'blah'}, content_type=None, ajax=False)
        self.assertEqual(response.status_code, 400)
        
    def test_add_new_client(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/add_new_client'
        data = {'client_name':'hren_s_gory', 'client_display_name':'blahblah', 'client_language':Language.objects.get(id=1).slug, 'client_emails':'test@test.fr, mail@host.com'}
        response = http_request(url, method='post', data=data, content_type=None)
        self.assertEqual(response.content, '{"errors": [], "success": true}')
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method='post', content_type=None, ajax=False)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', ajax=False)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', data={'blah':'blah'}, content_type=None, ajax=False)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='post', content_type=None)
        self.assertFalse(simplejson.loads(response.content)['success'])
        #test error when client already exists
        existing_client = Client.objects.get(id=1)
        data = {'client_name':existing_client.client_name, 'client_display_name':'blahblah', 'client_language':Language.objects.get(id=1).slug, 'client_emails':'test@test.fr, mail@host.com'}
        response = http_request(url, method='post', data=data, content_type=None, cookie={'lang':'en'})
        self.assertFalse(simplejson.loads(response.content)['success'])
        
    def test_update_client_info(self):
        #=======================================================================
        # Good request
        #=======================================================================
        existing_client = Client.objects.get(id=1)
        url='/rnr/update_client_info'
        new_name = 'must not be changed'
        new_display_name = 'blahblahblah'
        new_language = Language.objects.get(id=2).slug
        new_emails = 'test@test.fr, mail@host.com'
        data = {'slug':existing_client.slug,
                'client_update_name':new_name,
                'client_update_display_name':new_display_name,
                'client_update_language':new_language,
                'client_update_emails':new_emails}
        response = http_request(url, method='post', data=data, content_type=None)
        self.assertTrue(simplejson.loads(response.content)['success'])
        changed_client = Client.objects.get(id=1)
        changed_contacts = Contact.objects.filter(client = changed_client).values('contact_email')
        self.assertEqual(existing_client.client_name, changed_client.client_name)
        self.assertEqual(changed_client.client_display_name,new_display_name)
        self.assertEqual(changed_client.client_language.slug, new_language)
        self.assertEqual(new_emails.split(', '), [x['contact_email'] for x in changed_contacts])
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method='get')
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='post', ajax=False)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='post', data={'slug':existing_client.slug}, content_type=None)
        self.assertFalse(simplejson.loads(response.content)['success'])
        response = http_request(url, method='post', data={'slug':existing_client.slug, 'client_update_email':'blah'}, content_type=None)
        self.assertFalse(simplejson.loads(response.content)['success'])
        
    def test_del_client(self):
        #=======================================================================
        # Good requests
        #=======================================================================
        existing_client = Client.objects.get(id=2)
        url = '/rnr/del_client'
        response = http_request(url, method='post', data={'client_slug':existing_client.slug}, content_type=None)
        self.assertEqual(response.status_code, 200)
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method='get', content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='post', data={'blah':'blah'}, content_type=None)
        self.assertEqual(response.status_code, 400)
        
    def test_del_contact(self):
        #=======================================================================
        # Good request
        #=======================================================================
        existing_contact = Contact.objects.get(id=2)
        url = '/rnr/del_contact'
        response = http_request(url, method='post', data={'contact_slug':existing_contact.slug}, content_type=None)
        self.assertEqual(response.status_code, 200)
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method='get', content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='post', data={'blah':'blah'}, content_type=None)
        self.assertEqual(response.status_code, 400)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_ClientViews']
    unittest.main()