from . import models
from django.db.models import Q


def get_current_cart(request):
    token = request.COOKIES.get('cart', None)
    cart = None
    if request.user.is_authenticated():
        try:
            cart = models.Cart.objects.filter(user=request.user).filter(
                Q(order__isnull=True) | Q(
                    order__status=models.Order.STATUS_CHOICES.NEW)
            ).latest('created_at')
        except models.Cart.DoesNotExist:
            pass
    elif token:
        cart = models.Cart.objects.filter(token=token).filter(
            Q(order__isnull=True) | Q(
                order__status=models.Order.STATUS_CHOICES.NEW)
        ).first()
    return cart
