from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog, javascript_catalog
from django.conf.urls import (
    handler400, handler403, handler404, handler500
)

handler404 = 'core.views.page_404'
handler500 = 'core.views.page_500'

js_info_dict = {
    'packages': 'core+catalog+users+cart',
    'domain': 'django'
}

urlpatterns = [
    url(r'^sitemap\.htm$',
        TemplateView.as_view(template_name='sitemap.htm'),
        name='sitemap-htm'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
                                               content_type='text/plain'),
        name='robots'),
    url(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml',
                                                content_type='text/xml'),
        name='sitemap'),
    url(r'^admin/rosetta', include('rosetta.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/catalog/', include('catalog.urls', namespace='catalog-api')),
    url(r'^api/users/', include('users.urls', namespace='users-api')),
    url(r'^api/cart/', include('cart.urls', namespace='cart-api')),
    url(r'^api/core/', include('core.urls.api', namespace='core-api')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),
    url(r'^', include('core.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)