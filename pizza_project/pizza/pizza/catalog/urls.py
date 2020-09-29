from django.conf.urls import url

from .views import api


urlpatterns = [
    url(r'^products$', api.ProductListView.as_view(), name='product_list'),
    url(r'^products/actions$', api.ProductActionListView.as_view(), name='product_action_list')
]