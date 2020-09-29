from django.conf.urls import url

from ..views.api import ActionsListView, AvailableStreetListView, LocationListView


urlpatterns = [
    url(r'^actions$', ActionsListView.as_view()),
    url(r'^streets$', AvailableStreetListView.as_view()),
    url(r'^locations$', LocationListView.as_view()),
]
