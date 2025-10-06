# stagepass/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# NEW: sitemap + robots
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from events.sitemaps import EventSitemap  # you'll create events/sitemaps.py

sitemaps = {
    "events": EventSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),

    # apps
    path("", include("core.urls")),
    path("events/", include("events.urls")),
    path("", include("django.contrib.auth.urls")),
    path("orders/", include("orders.urls")),
    path("accounts/", include("accounts.urls")),
    
    # NEW: SEO
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_txt"),
]

# serve static files in DEBUG (ok for local dev)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
