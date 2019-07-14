import time

from celery import Celery
# from app import configured_app
from marrow.mailer import Mailer

import secret
from config import admin_mail

celery = Celery('tasks', backend='redis://localhost', broker='redis://localhost')


# app = configured_app()

def configured_mailer():
    config = {
        # 'manager.use': 'futures',
        'transport.debug': True,
        'transport.timeout': 1,
        'transport.use': 'smtp',
        'transport.host': 'smtp.exmail.qq.com',
        'transport.port': 465,
        'transport.tls': 'ssl',
        'transport.username': admin_mail,
        'transport.password': secret.mail_password,
    }
    m = Mailer(config)
    m.start()
    return m


mailer = configured_mailer()


@celery.task
def send_async_simple(subject, author, to, plain):
    m = mailer.new(
        subject=subject,
        author=author,
        to=to,
    )
    m.plain = plain
    mailer.send(m)
    time.sleep(10)


@celery.task(bind=True)
def send_async(self, subject, author, to, plain):
    try:
        m = mailer.new(
            subject=subject,
            author=author,
            to=to,
        )
        m.plain = plain
        mailer.send(m)
        # time.sleep(10)
        # raise ValueError('tetest')
    except Exception as exc:
        # 3秒重试一次 最多重试5次
        raise self.retry(exc=exc, countdown=3, max_retries=5)
