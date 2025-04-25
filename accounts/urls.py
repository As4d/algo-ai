from django.urls import path
from . import views

urlpatterns = [
    path('api/set-csrf-token', views.set_csrf_token, name='set_csrf_token'),
    path('api/login', views.login_view, name='login'),
    path('api/logout', views.logout_view, name='logout'),
    path('api/user', views.user, name='user'),
    path('api/register', views.register, name='register'),
    path('api/profile', views.get_profile, name='get_profile'),
    path('api/profile/update', views.update_profile, name='update_profile'),
    path('api/profile/change-password', views.change_password, name='change_password'),
]
