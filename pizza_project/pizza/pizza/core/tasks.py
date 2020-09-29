# -*- coding: utf-8 -*-
import logging

from django.conf import settings

from celery_app import app
from core.devinotele import RestApi, TimeoutError

logger = logging.getLogger(__name__)


class MaxRetryExceeded(Exception):
    pass


@app.task()
def send_sms_message(recipient, message, repeated=1):
    if repeated >= settings.SMS_SERVICE_MAX_REPEAT:
        raise MaxRetryExceeded('Too many attempts to send sms. Decline task')

    if not settings.SMS_SERVICE_DEBUG:
        (login, password), host = settings.SMS_SERVICE_CREDENTIALS, settings.SMS_SERVICE_HOST

        client = RestApi(login, password, host=host)

        try:
            res = client.send_message(
                settings.SMS_SERVICE_SOURCE,
                recipient,
                message
            )
            logger.debug('Response: %s' % str(res))
        except TimeoutError:
            kwargs = {
                'recipient': recipient,
                'message': message,
                'repeated': repeated + 1
            }
            msg_ptr = 'Cannot send sms. Retry. recipient: {}, ' \
                      'text: {}, repeat: {} of {}'
            msg = msg_ptr.format(recipient, message, repeated,
                                 settings.SMS_SERVICE_MAX_REPEAT)
            logger.info(msg)
            send_sms_message.apply_async(
                kwargs=kwargs,
                countdown=settings.SMS_SERVICE_COUNTDOWN_SEC
            )
    else:
        logger.debug('Sms was sent. recipient: {number}; text: {text}'.format(
            number=recipient, text=message
        ))
