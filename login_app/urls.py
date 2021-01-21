from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('home', views.home),
    path('register', views.register),
    path('login', views.login),
    path('logout/', views.logout),
    path('register_form', views.register_form),
    path('users', views.users),
    path('users/<id>', views.user_profile),
    path('users/<id>/edit', views.user_edit),
    path('edituserinfo', views.edit_user_info),
    path('changepassword', views.change_password),
    path('makeadmin', views.make_admin),
    path('adduser', views.add_user),
    path('adduserpost', views.add_user_post),
    path('search', views.search),
    path('request', views.request)
]