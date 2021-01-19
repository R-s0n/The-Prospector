from django.urls import path, include

urlpatterns = [
    path('', include('login_app.urls')),
]
