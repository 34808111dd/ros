'''
Created on Aug 22, 2014

@author: Coeurl
'''

import smtplib
import email
from email.mime.text import MIMEText
from processor import settings
from rnr.models import NotificationState, Contact
import datetime
import time

class EmailProcessor(object):
    '''
    Email processor object. Singletone
    Has it's own queue for notification_obj processing, allows adding in queue.
    All messages in queue should be sent in one tcp session.
    
    !Note
    There is a limit (quota) set on our mail server, so, we should sent about 5 mails in one session, then wait, then reestablish session.
    All mails that was not sent will have status "sent_error" and displayed in red.
    
    SMTPServerDisconnected
    
    
    
    '''
    _single = None
    notifications_queue = []
    sending_now = False
    _reset_queue = False
    
    notif_sent_state = NotificationState.objects.get(notificationstate_name='sent')
    notif_err_state = NotificationState.objects.get(notificationstate_name='sent_error')
        
    
    def __new__(cls,*args, **kargs):
        if not cls._single:
            cls._single = super(EmailProcessor, cls).__new__(cls, *args, **kargs)
        return cls._single
    
    #def __init__(self):
    #    self.notifications_queue = []
        
    def add_to_queue(self, notification_django_obj):
        print "adding to queue", notification_django_obj
        if notification_django_obj not in self.notifications_queue:
            self.notifications_queue.append(notification_django_obj)
        
    def reset_queue(self):
        
        for _x in self.notifications_queue:
            _x.notification_state = self.notif_err_state
            _x.save()
        self.notifications_queue=[]
        
        
    def send_all(self):
        '''
        send all messages in one tcp session
        server does not allow to send more then 4 messages in one session
        '''
        
        if not self.sending_now:
            self.sending_now = True
            while len(self.notifications_queue) > 0:
                if self._reset_queue:
                    print "breaking large queue"
                    break
                    
                #get first amount of notifications in queue
                small_queue = self.notifications_queue[:settings.max_mesage_queue]
                server = smtplib.SMTP()
                try:
                    server.connect(settings.smtp_server_name,settings.smtp_server_port)
                    server.ehlo()
                    server.starttls()
                    server.login(settings.smtp_server_login, settings.smtp_server_password)
                    for notification_obj in small_queue:
                        if self._reset_queue:
                            print "breaking small queue"
                            break
                        local_msg = MIMEText(notification_obj.notification_complete_text, _charset="utf-8")
                        #Debug purpose
                        client_contact_list = [x["contact_email"] for x in Contact.objects.filter(client=notification_obj.notification_client).values('contact_email')]
                        print client_contact_list
                        tolist = ['alexander.shtyrkov@rt.ru', 'mnc@rt.ru']
                        
                        local_msg['From'] = settings.message_from
                        local_msg['To'] = email.Utils.COMMASPACE.join(tolist)
                        local_msg['CC'] = settings.message_from
                        local_msg['Subject'] = notification_obj.notification_subject
                        local_msg['Reply-To'] = settings.message_reply_to
                        print "sending", notification_obj
                        try:
                            server.sendmail('alexander.shtyrkov@rt.ru',tolist,local_msg.as_string())
                            notification_obj.notification_send_date = datetime.datetime.now()
                            notification_obj.notification_state = self.notif_sent_state
                            notification_obj.save()
                            self.notifications_queue.remove(notification_obj)
                        except Exception as error:
                            print "server unexpectedly disconnected, closing, waiting."
                            print "error", error
                    server.quit()
                    
                except Exception as e:
                    print "got exception", e
                    time.sleep(settings.smtp_server_retry_timeout)
                print "done for small piece of queue, disconnecting form server"
            print "done all work. self.sending_now = False"
            
            self.reset_queue()
            self._reset_queue = False
            self.sending_now = False
            
        else:
            print "already sending messages", self.notifications_queue
