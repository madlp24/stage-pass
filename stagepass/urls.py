# stagepass/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import CustomLoginView
from django.contrib.auth import views as auth_views

# NEW: sitemap + robots
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from events.sitemaps import EventSitemap  # you'll create events/sitemaps.py

sitemaps = {
    "events": EventSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),

    # Custom login must come BEFORE django.contrib.auth.urls
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Your apps
    path("", include("core.urls")),
    path("events/", include("events.urls")),
    path("orders/", include("orders.urls")),
    path("accounts/", include("accounts.urls")),

    # Django auth URLs WITHOUT login/logout
    path("", include("django.contrib.auth.urls")),

    # SEO
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_txt"),
]


# serve static files in DEBUG (ok for local dev)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=getattr(settings, "MEDIA_ROOT", None))
