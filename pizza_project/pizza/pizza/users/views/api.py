from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..tasks import send_email_confirmation
from .. import serializers
from .. import models


class LoginUserView(APIView):

    serializer_class = serializers.AuthSerializer

    def post(self, request):

        if request.user.is_authenticated():
            data = serializers.UserSerializer(request.user).data
            return Response(data)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)

        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        data = serializers.UserSerializer(user).data
        return Response(data)


class LogoutUserView(APIView):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
        return Response()


class RegistrationView(APIView):

    serializer_class = serializers.UserRegistrationSerializer

    @transaction.atomic
    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.PhoneVerification.attempts(session=request.session.session_key) <= 0:
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        if models.PhoneVerification.attempts(phone=serializer.validated_data['phone']) <= 0:
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        user = models.AppUser.objects.filter(
            phone=serializer.validated_data['phone']
        ).last()

        if user:
            if user.is_active:
                return Response(status=status.HTTP_403_FORBIDDEN)
            instance = user
        else:
            instance = serializer.save(is_active=False)

        request.session['user_id'] = str(instance.id)
        request.session.save()
        record = models.PhoneVerification.objects.create(
            user=instance,
            phone=instance.phone,
            session=request.session.session_key
        )
        instance.set_password(record.sms_code)
        instance.save(update_fields=['password'])
        instance.sms_tpl_user('registration', {'password': record.sms_code})
        return Response({
            'token': record.token
        })


class UserRegistration2faView(APIView):

    serializer_class = serializers.SMSCodeSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid(raise_exception=True):
            token = request.data.get('token', None)
            if token:
                record, cancelled = models.PhoneVerification.handle_sms_code_failed(request.session.session_key, token)
                if cancelled:
                    return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        record = serializer.validated_data
        user_id = request.session.get('user_id', None)
        if user_id is None:
            record.cancel()
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = authenticate(request, user_id=user_id, check_can_auth=False)

        if user is None:
            record.cancel()
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user.is_active = True
        user.save(update_fields=['is_active'])
        record.mark_as_verified()

        login(request, user=user)

        data = serializers.UserSerializer(user).data
        return Response(data)


class PasswordRecoverView(APIView):

    serializer_class = serializers.PasswordRecoverSerializer

    @transaction.atomic()
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data

        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not user.can_change_password():
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        new_password = user.set_light_password()
        user.save(update_fields=['password'])
        user.sms_tpl_user('recover', {'password': new_password})

        return Response()


class ProfileDataView(generics.RetrieveUpdateAPIView):

    serializer_class = serializers.UserSerializer

    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        return super(ProfileDataView, self).get(request, *args, **kwargs)

    @method_decorator(login_required(login_url='/'))
    def put(self, request, *args, **kwargs):
        return super(ProfileDataView, self).put(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_email = instance.email
        profile_serializer = self.get_serializer(instance=instance, data=request.data)
        password_serializer = serializers.PasswordChangeSerializer(data=request.data, context={'request': request, 'view': self})

        profile_serializer.is_valid(raise_exception=True)
        password_serializer.is_valid(raise_exception=True)

        email_confirmed = instance.email_confirmed
        new_email = profile_serializer.validated_data['email']
        if old_email != new_email:
            email_confirmed = False
            if new_email:
                send_email_confirmation.apply_async(args=[instance.id])

        user = profile_serializer.save(email_confirmed=email_confirmed)

        new_password = password_serializer.validated_data

        if new_password:
            user.set_password(new_password)
            user.save(update_fields=['password'])
            user = authenticate(request, username=user.phone, password=new_password)
            login(request, user)

        return Response(status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return serializers.UserSerializer
        return serializers.ProfileDataSerializer

    def get_object(self):
        return self.request.user
