from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from core.models import Location


class GeoLocationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        location_id = request.COOKIES.get(settings.LOCATION_COOKIE_NAME, None)
        request.geo_location = None
        if location_id:
            try:
                request.geo_location = Location.objects.get(
                    id=location_id, config__isnull=False, is_active=True
                )
            except Location.DoesNotExist:
                pass

        request.empty_location = request.geo_location is None

        if request.empty_location:
            if request.user.is_authenticated() and request.user.location \
                    and request.user.location.is_active:
                request.geo_location = request.user.location
                try:
                    request.geo_location.config
                except:
                    request.geo_location = Location.objects.get(
                        id=settings.DEFAULT_LOCATION_ID)
            else:
                request.geo_location = Location.objects.get(id=settings.DEFAULT_LOCATION_ID)
            request.empty_location = Location.objects.filter(
                is_active=True, config__isnull=False).count() > 1
