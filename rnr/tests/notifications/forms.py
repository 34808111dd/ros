'''
Created on Jan 7, 2015

@author: Coeurl
'''


import unittest
from rnr.models import Client, Work, NotificationTemplate

from rnr.forms import NotificationForm

class test_NotificationForm(unittest.TestCase):
    valid_form_data={'notification_client': Client.objects.get(id=1).slug,
           'notification_work': Work.objects.get(id=1).slug,
           'notification_template': NotificationTemplate.objects.get(id=1).slug,
           'notification_complete_text': 'blah'}
        
    def test_NotificationForm_gen(self):
        '''
        '''
        notif_form = NotificationForm(self.valid_form_data)
        self.assertTrue(notif_form.is_valid(), "NotificationForm validation failed with data: "+str(self.valid_form_data))
        
        valid_form_data = {}
        notif_form = NotificationForm(valid_form_data)
        self.assertFalse(notif_form.is_valid())
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testWorkView']
    unittest.main()