from django.urls import path
from . import views
from .views import dashboard_view

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.login_view, name="register"),
    path('dashboard/', dashboard_view, name='dashboard'),
]
