"""lumino_learn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from users.urls import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("users/", include("users.urls")),
    path('', TemplateView.as_view(template_name="index.html"), name='home'),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("student_dashboard/", views.student_dashboard_view, name="student_dashboard"),
    path("educator_dashboard/", views.educator_dashboard_view, name="educator_dashboard"),
    path("admin_dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("login/", views.logout_view, name="logout"),
]

# For serving static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)