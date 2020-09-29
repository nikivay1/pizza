from django.conf.urls import url

from .views import api


urlpatterns = [
    url(r'^login$', api.LoginUserView.as_view(), name='login'),
    url(r'^logout$', api.LogoutUserView.as_view(), name='logout'),
    url(r'^signup$', api.RegistrationView.as_view(), name='signup'),
    url(r'^signup/2fa$', api.UserRegistration2faView.as_view(), name='signup_2fa'),
    url(r'^password/recover$', api.PasswordRecoverView.as_view(), name='password_recover'),
    url(r'^profile$', api.ProfileDataView.as_view(), name='profile')
]