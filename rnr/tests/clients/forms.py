'''
Created on Jan 8, 2015

@author: Coeurl
'''
import unittest
from rnr.forms import ClientForm, UpdateClientForm
from rnr.models import Language

class TestClientForms(unittest.TestCase):


    def testClientForm(self):
        data = {'client_name':'blah',
                'client_display_name':'blah',
                'client_language':Language.objects.get(id=1).slug,
                'client_emails':'blah@blah.bl',
                }
        new_form = ClientForm(data)
        self.assertTrue(new_form.is_valid())
        data['client_emails']='blah, blah'
        new_form = ClientForm(data)
        self.assertFalse(new_form.is_valid())
        self.assertIn('client_emails', new_form.errors.keys())
        
        data['client_language']='blah'
        new_form = ClientForm(data)
        self.assertFalse(new_form.is_valid())
        self.assertIn('client_language', new_form.errors.keys())
        
    def testUpdateClientForm(self):
        data = {'client_update_name':'blah',
                'client_update_display_name':'blah',
                'client_update_language':Language.objects.get(id=1).slug,
                'client_update_emails':'blah@blah.bl',
                }
        new_form = UpdateClientForm(data)
        self.assertTrue(new_form.is_valid())
        
        data['client_emails']='blah, blah'
        new_form = ClientForm(data)
        self.assertFalse(new_form.is_valid())
        self.assertIn('client_emails', new_form.errors.keys())
        
        data['client_language']='blah'
        new_form = ClientForm(data)
        self.assertFalse(new_form.is_valid())
        self.assertIn('client_language', new_form.errors.keys())
        
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()