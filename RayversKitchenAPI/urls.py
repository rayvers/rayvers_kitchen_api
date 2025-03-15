
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.views import HomeAPIViewList as HomeView
from django.contrib import admin
from dashboard import views as auth_views

admin.site.site_header = "Reyvers Kitchen Administration"
admin.site.site_title = "Reyvers Kitchen Admin Portal"
admin.site.index_title = "Welcome to Reyvers Kitchen Admin Portal"

urlpatterns = [
    path("", HomeView.as_view(), name="home_api_view"),
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls"), name="authentication"),
    path("api/", include("app.urls"), name="app"),
    path("dashboard/", include("dashboard.urls"), name="dashboard"),

    # Dashboard Auth Views
    path('login/', auth_views.login_view, name="login"),
    path('register/', auth_views.register, name="register"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


