from django.urls import path, include

urlpatterns = [
    path('api/mathlock/', include('credits.urls')),
]
