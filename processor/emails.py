'''
Created on Aug 22, 2014

@author: Coeurl
'''

import smtplib
import email
from email.mime.text import MIMEText
from processor import settings
from rnr.models import NotificationState
import datetime


class EmailProcessor(object):
    '''
    Email processor object.
    Has it's own queue for notification_obj processing, allows adding in queue.
    All messages in queue should be sent in one tcp session.
    
    !Note
    There is a limit (quota) set on our mail server, so, we should sent about 5 mails in one session, then wait, then reestablish session.
    All mails that was not sent will have status "sent_error" and displayed in red.
    
    '''
    
    def __init__(self):
        self.notifications_queue = []
        
    def add_to_queue(self, notification_django_obj):
        self.notifications_queue.append(notification_django_obj)
        
    def send_queue(self):
        '''
        send all messages in one tcp session
        '''
        
        notif_sent_state = NotificationState.objects.get(notificationstate_name='sent')
        notif_err_state = NotificationState.objects.get(notificationstate_name='sent_error')

        '''
        server does not allow to send more then 4 messages in one session
        '''
        while len(self.notifications_queue) > 0:
            #get first amount of notifications in queue
            small_queue = self.notifications_queue[:settings.max_mesage_queue]
            server = smtplib.SMTP()
            server.connect(settings.smtp_server_name,settings.smtp_server_port)
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_server_login, settings.smtp_server_password)
            
            for notification_obj in small_queue:
                local_msg = MIMEText(notification_obj.notification_complete_text, _charset="utf-8")
                #Debug purpose
                tolist = ['alexander.shtyrkov@rt.ru', 'mnc@rt.ru']
                local_msg['From'] = settings.message_from
                local_msg['To'] = email.Utils.COMMASPACE.join(tolist)
                local_msg['Subject'] = notification_obj.notification_subject
                local_msg['Reply-To'] = settings.message_reply_to
                print "sending", notification_obj
                try:
                    server.sendmail('alexander.shtyrkov@rt.ru',tolist,local_msg.as_string())
                    notification_obj.notification_send_date = datetime.datetime.now()
                    notification_obj.notification_state = notif_sent_state
                    notification_obj.save()
                    self.notifications_queue.remove(notification_obj)
                except Exception as error:
                    for _x in self.notifications_queue:
                        _x.notification_state = notif_err_state
                        _x.save()
                    
                    raise error
            server.quit()
#            time.sleep()
            print "done disconnecting"
