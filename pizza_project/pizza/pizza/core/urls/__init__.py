from django.conf.urls import url

from ..views import (
    IndexView,
    ProfileView,
    OrderDetailView,
    EmailConfirm,
    ActionView,
    PolicyTerms,
    LocationSetView
)


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^policy$', PolicyTerms.as_view(), name='policy'),
    url(r'^profile$', ProfileView.as_view(), name='profile'),
    url(r'^order/(?P<number>.+)/(?P<hash>.+)$', OrderDetailView.as_view(), name='order-detail'),
    url(r'^order/(?P<number>.+)/(?P<hash>.+)$', OrderDetailView.as_view(), name='order-detail'),
    url(r'^email/confirm/$', EmailConfirm.as_view(), name='email-confirm'),
    url(r'^actions/$', ActionView.as_view(), name='actions'),
    url(r'^set-location/$', LocationSetView.as_view(), name='set_location')
]
