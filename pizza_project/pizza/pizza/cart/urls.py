from django.conf.urls import url
from .views import api


urlpatterns = [
    url(r'^$', api.CartDetailView.as_view()),
    url(r'^add$', api.AddProductView.as_view()),
    url(r'^item/(?P<pk>\d+)$', api.ItemCartUpdateView.as_view()),
    url(r'^order$', api.OrderCreateView.as_view()),
    url(r'^order/address$', api.AddressUpdateView.as_view()),
    url(r'^order/(?P<pk>\d+)/link', api.OrderPaymentLinkView.as_view()),
    url(r'^clean$', api.CleanCartView.as_view())
]
