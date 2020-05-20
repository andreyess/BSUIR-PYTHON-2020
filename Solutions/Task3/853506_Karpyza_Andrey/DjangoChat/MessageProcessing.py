import hashlib
from jinja2 import Template
from django.core.mail import send_mail
from multiprocessing import Process
from threading import Thread


class QueueThread(Thread):

    def run(self):
        while len(MessageQueue.queue) > 0:
            MessageQueue.queue[0].start()
            MessageQueue.queue[0].join()
            MessageQueue.queue.pop(0)


class MessageQueue:
    MessageTemplate = Template('''Hello, {{ username }}!
    With your email {{ email }} did an account on our website My Blog registered.
    If it was you - for continuing of registration you must go on the next link: {{ link }}
    The time of sending of this message: {{ time }}
    Have a nice day!''')

    queue = []
    _messageQueueProcessing = QueueThread()

    @classmethod
    def AddMessageInQueue(cls, instance):
        instance.url = hashlib.sha1(bytes(instance.profile.user.username, 'utf-8')).hexdigest()
        msg = cls.MessageTemplate.render(username=instance.profile.user.username,
                                     link='http://127.0.0.1:8000/register/confirmation/{}'.format(instance.url),
                                     time=instance.time, email=instance.profile.user.email)
        cls.queue.append(Process(target=send_mail, args=('Email confirmation on My Blog',
                                                         msg, instance.profile.user.email, [instance.profile.user.email])))
        instance.sended = True
        instance.save()
        if not cls._messageQueueProcessing.is_alive():
            cls._messageQueueProcessing = QueueThread()
            cls._messageQueueProcessing.start()
