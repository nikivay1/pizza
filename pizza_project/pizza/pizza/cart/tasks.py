import logging

from celery.task import periodic_task
from django.utils import timezone
from celery_app import app
from core.utils import get_status_sb_order


logger = logging.getLogger(__name__)


@periodic_task(run_every=timezone.timedelta(minutes=1))
def fetch_order_status():
    from cart.models import Order
    current_time = timezone.now() - timezone.timedelta(days=1)
    for order in Order.objects.filter(
            payment_type=Order.PAYMENT_TYPE.ONLINE,
            sb_started_at__gte=current_time,
            online_status__in=[
                Order.TRANSACTION_STATUS.INITIAL_BY_EMITENT,
                Order.TRANSACTION_STATUS.REGISTERED
            ]):
        status = get_status_sb_order(order.sb_remote_id)

        if status is not None:
            order.online_status = status
            if status == Order.TRANSACTION_STATUS.SUCCESS:
                order.status = Order.STATUS_CHOICES.CONFIRMED
                order.started_at = timezone.now()
                order.expired_at = order.address.location.config.order_timeout + order.started_at
                order.send_notification()
            elif status not in [
                Order.TRANSACTION_STATUS.REGISTERED,
                Order.TRANSACTION_STATUS.INITIAL_BY_EMITENT
            ]:
                order.status = Order.STATUS_CHOICES.FAILED
            order.save()
