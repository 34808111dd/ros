'''
Created on Dec 23, 2014

@author: Coeurl
'''
#from django.test import Client
from django.core.exceptions import ObjectDoesNotExist
import Cookie
import unittest
import simplejson
import json
from rnr.models import Work, Notification, Client, NotificationType
from processor.shortcuts import http_request, success_response

class TestNotificationViews(unittest.TestCase):

    def test_get_notifications_json(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/get_notifications_json'
        work_slug = Work.objects.get(id=1).slug
        data={'work_slug':work_slug}
        response = http_request(url, method='get', data=data, cookie={"lang":"en"})
        self.assertEqual(len(simplejson.loads(response.content)), 17)
        
        data = {'work_slug':work_slug, 'notification_type':'notification'}
        response = http_request(url, method='get', data=data)
        self.assertEqual(len(simplejson.loads(response.content)), 17)
        
        #=======================================================================
        # Bad request, return Http400 on error
        #=======================================================================
        data = {'blah':'blah'}
        response = http_request(url, method='get', data=data, cookie={"lang":"en"})
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='post', data=data, cookie={"lang":"en"})
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method='get', ajax=False, cookie={"lang":"en"})
        self.assertEqual(response.status_code, 400)
        
    def test_get_notification_type_all_json(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/get_notification_type_all_json'
        response = http_request(url, method = 'get')
        self.assertEqual(len(simplejson.loads(response.content)), 2)
        #=======================================================================
        # Bad request
        #=======================================================================
        response = http_request(url, method = 'post')
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', data={'blah':'blah'})
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', ajax=False)
        self.assertEqual(response.status_code, 400)
        
    def test_del_notification(self):
        url = '/rnr/del_notification'
        notification_slug = Notification.objects.get(id=100).slug
        data = {'notification_slug':notification_slug}
        #=======================================================================
        # Good request
        #=======================================================================
        response = http_request(url, method = 'post', data=data, content_type = None)
        self.assertEqual(response.content, success_response)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(ObjectDoesNotExist):
            Notification.objects.get(slug=notification_slug)
        #=======================================================================
        # Bad request
        #=======================================================================
        response = http_request(url, method = 'get', data=data, content_type = None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', data={'':''}, content_type = None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'get', ajax=False)
        self.assertEqual(response.status_code, 400)
        
    def test_view_notification(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/view_notification'
        notification = Notification.objects.get(id=20)
        data = {'notification_slug':notification.slug}
        response = http_request(url, method = 'get', data=data, cookie={"lang":"en"})
        self.assertEqual(simplejson.loads(response.content),\
                         {'notification_subject':notification.notification_subject,\
                          'notification_complete_text':notification.notification_complete_text})
        self.assertEqual(response.status_code, 200)
        #=======================================================================
        # Bad request
        #=======================================================================
        response = http_request(url, method = 'get', data={'blah':'blah'}, cookie={"lang":"en"})
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'get')
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'get', ajax=False)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', data={'blah':'blah'}, cookie={"lang":"en"})
        self.assertEqual(response.status_code, 400)
        
    def test_save_notification(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/save_notification'
        work = Work.objects.get(id=11)
        data = {'notification_subject':'works on net - 00/1400950',
'notification_text':'blah 00/1400950',
'test': json.dumps({"client_slug":"3A45A2782c4f","work_slug":work.slug,"notification_type_slug":"19FCA9f3c8C8","MW":[{"mw_name":"","mw_outages":[]}]})}
        response = http_request(url, method = 'post', data=data, content_type=None)
        self.assertEqual(response.content, "ok")
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method = 'get', data=data, content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', data={'blah':'blah'}, content_type=None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', data=data)
        self.assertEqual(response.status_code, 400)
        
    def test_update_notification(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/update_notification'
        notif_object = Notification.objects.get(id=30)
        data =  {'notification_slug':notif_object.slug, 'message_subject':notif_object.notification_subject+'test',\
                'message_body':notif_object.notification_complete_text}
        response = http_request(url, method = 'post', data=data, content_type = None)
        self.assertEqual(response.status_code, 200)
        changed_notification = Notification.objects.get(id=30)
        self.assertEqual(changed_notification.notification_subject, notif_object.notification_subject+'test')
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method = 'get', data=data, content_type = None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', content_type = None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'get')
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post', data=data)
        self.assertEqual(response.status_code, 400)
        
    def test_gen_cancel(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/gen_cancel'
        work_obj = Work.objects.get(id=10)
        count_before = Notification.objects.filter(notification_work=work_obj).count()
        data = {'work_slug':work_obj.slug}
        response = http_request(url, method = 'post', data=data, content_type = None)
        count_after = Notification.objects.filter(notification_work=work_obj).count()
        self.assertEqual(count_before*2, count_after)
        response = http_request(url, method = 'post', data=data, content_type = None)
        #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method = 'get', data=data, content_type = None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post')
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'get', data=data)
        self.assertEqual(response.status_code, 400)
    def test_gen_notification(self):
        #=======================================================================
        # Good request
        #=======================================================================
        url = '/rnr/gen_notification'
        data = {"test":simplejson.dumps({"client_slug":"b4037eBe0f13","work_slug":"Ece691DB6EBa","notification_type_slug":"4ed83a1A73f0","MW":[{"mw_name":"01/07/2015 01:00 - 01/07/2015 02:00","mw_outages":[{"outage_type":"9Cb6768BAb7F","outage_channel":"3123"}]}]})}
        response = http_request(url, method = 'post', data=data, content_type = None)
        self.assertEqual(response.status_code, 200)
        
        json_obj= simplejson.loads(response.content)
        
        response_body = json_obj["body"]
        response_subj = json_obj["subject"]
        
        target_body = u"Dear colleagues Global \u0421rossing,\r\n\r\nPlease be informed about the addition to the maintenance below.\r\n\r\nMaintenance 08/1400913\r\n\r\nLocation: Rostelecom's network\r\nRegion: Siberia region\r\n\r\nMaintenance window: Start Time: 21.08.2014 06:00 (UTC)\r\nMaintenance window: Stop Time: 21.08.2014 08:30 (UTC)\r\n\r\n------------------------------------------------------------------\r\n01/07/2015 01:00 - 01/07/2015 02:00\nService impact: The service will be interrupted during the whole maintenance window.\n---\n3123\n\n\r\n------------------------------------------------------------------\r\n\r\nPlease accept our apologies for any inconvenience. For any further enquiries please contact us: vipservice@rt.ru or per phone +7 (499)  999-8285, +7 (499) 999 8143\r\n\r\nSales Assistance and Service Support\r\nfor Strategic Accounts Corporate Customer Sales Department OJSC \u201cRostelecom\u201d\r\nTel.: +7 499 999-8283 ext. 4271\r\n+7 495 539-5746\r\nMob.: +7 919 991-3057\r\ne-mail: Vipservice@rt.ru"
        target_subj = "Maintenance Rostelecom\u2019s network - 08/1400913"
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body, target_body)
                #=======================================================================
        # Bad requests
        #=======================================================================
        response = http_request(url, method = 'get', data=data, content_type = None)
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'post')
        self.assertEqual(response.status_code, 400)
        response = http_request(url, method = 'get', data=data)
        self.assertEqual(response.status_code, 400)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testNotificationViews']
    unittest.main()