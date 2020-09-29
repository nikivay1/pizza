from catalog import models as catalog_models
from core import models as core_models


def categories_processor(request):
    return {
        'category_list': catalog_models.Category.objects.all()
    }


def location_list(request):
    return {
        'locations': core_models.Location.objects.filter(
            is_active=True, config__isnull=False
        )
    }


def site_config(request):
    return {
        'social_links': core_models.SocialLink.objects.all(),
        'site_config': request.geo_location.config,
        'empty_location': request.empty_location,
        'current_location': request.geo_location
    }
