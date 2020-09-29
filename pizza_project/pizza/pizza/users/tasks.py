import telegram

from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from celery_app import app
from core.tasks import send_sms_message


@app.task()
def send_order_notifications(phone_enabled: bool,
                             phone_recipient: str,
                             telegram_enabled: bool,
                             telegram_recipient: str,
                             order_id: int):
    from cart.models import Order
    order = Order.objects.get(id=order_id)
    if phone_enabled:
        send_tpl_sms_message.delay(
            phone_recipient,
            'order_sms_notification',
            {'order': order}
        )
    if telegram_enabled:
        send_tpl_telegram_message.delay(
            telegram_recipient,
            'order_telegram_notification',
            {'order': order}
        )


@app.task()
def send_tpl_sms_message(recipient: str, tpl_or_raw: str, context=None, raw=False):
    from core.models import SMSTemplate

    context = context or {}
    if not raw:
        sms_tpl = SMSTemplate.get_slag(tpl_or_raw)
        ctx = Context(context)
        message = Template(sms_tpl.text).render(ctx)
    else:
        message = tpl_or_raw

    if recipient:
        send_sms_message.delay(
            recipient,
            message
        )


@app.task()
def send_tpl_telegram_message(recipient: str, tpl_or_raw: str, context=None, raw=False):
    from core.models import SMSTemplate

    context = context or {}
    context.update({
        'domain_url': settings.DOMAIN_NAME
    })
    if not raw:
        sms_tpl = SMSTemplate.get_slag(tpl_or_raw)
        ctx = Context(context)
        message = Template(sms_tpl.text).render(ctx)
    else:
        message = tpl_or_raw

    if recipient:
        bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
        bot.send_message(
            chat_id=recipient,
            text=message
        )


def send_email_message(subject, message, from_email, to, **kwargs):
    pass


@app.task()
def send_email_confirmation(user_id):
    from users.models import AppUser
    user = AppUser.objects.get(id=user_id)
    email_url = user.get_email_confirm_url()

    text_message = render_to_string('email/confirmation.txt', {
        'domain': settings.DOMAIN_NAME,
        'url': email_url,
        'user': user
    })

    html_message = render_to_string('email/confirmation.html', {
        'domain': settings.DOMAIN_NAME,
        'url': email_url,
        'user': user
    })

    if email_url:
        send_mail(_("Email confirmation"), text_message, settings.DEFAULT_FROM_EMAIL, [user.email],
                  html_message=html_message)

