import base64
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView
from django.conf import settings

from catalog import models as catalog_models
from cart import models as cart_models, utils
from core.models import Location
from users.models import AppUser


class MetricMixin(object):
    def get_context_data(self, **kwargs):
        context = super(MetricMixin, self).get_context_data(**kwargs)
        context['metric_include'] = True
        return context


class IndexView(MetricMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['categories'] = catalog_models.Category.objects.all()
        return context


class ActionView(MetricMixin, TemplateView):
    template_name = 'action.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('index')
        return super(ProfileView, self).get(request, *args, **kwargs)


class OrderDetailView(DetailView):
    template_name = "order.html"

    def get_object(self, queryset=None):
        order = get_object_or_404(cart_models.Order,
                                  number=self.kwargs['number'])
        hash_str = self.kwargs['hash']
        if order.get_hash() != hash_str:
            raise Http404()
        return order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['seconds'] = self.object.get_seconds()
        print(self.object.started_at)
        print(self.object.expired_at)
        return context


class EmailConfirm(TemplateView):
    template_name = 'email_confirm.html'

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        hash_str = request.GET.get('token', None)

        message = _("User wasn't  found")

        if hash_str:

            try:
                decoded_data = base64.b64decode(hash_str).decode()
            except:
                pass
            else:
                user_id, email, token = decoded_data.split(':')
                try:
                    user = AppUser.objects.get(pk=user_id, email=email)
                except AppUser.DoesNotExist:
                    pass
                else:
                    user_token = user.get_email_hash()
                    if user_token == token and not user.email_confirmed:
                        user.email_confirmed = True
                        user.save()
                        message = _("Your email successfully confirmed")
                    else:
                        message = _("Your email already confirmed")

        context = self.get_context_data(**kwargs)
        context['message'] = message
        return self.render_to_response(context)


class PolicyTerms(TemplateView):
    template_name = 'policy.html'


class LocationSetView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LocationSetView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        next_url = request.POST.get('next_url', '/')
        if request.POST:
            if Location.objects.filter(pk=request.POST.get('location', None),
                                       config__isnull=False).exists():
                location = get_object_or_404(Location,
                                             pk=request.POST.get('location',
                                                                 None))
            else:
                return redirect('/')
            if request.user.is_authenticated():
                user = request.user
                user.location = location
                user.save(update_fields=['location'])
            response = HttpResponseRedirect(next_url)
            response.set_cookie(settings.LOCATION_COOKIE_NAME,
                                str(location.id),
                                expires=timezone.now() + timezone.timedelta(
                                    days=100))
            cart = utils.get_current_cart(request)
            if cart:
                cart.items.exclude(price__product__location_id=location.id) \
                    .delete()
            return response
        return HttpResponseRedirect(next_url)


def page_404(request):
    response = render(request, 'page_error.html', {
        'text': '404, страница не найдена! '
                'Через несколько секунд вы будете '
                'перенаправлены на главную страницу!',
        'page_redirect': reverse('index')
    })
    response.status_code = 404
    return response


def page_500(request):
    response = render(request, 'page_error.html',
                      {'text': 'Внутренняя ошибка сервера.'})
    response.status_code = 500
    return response
