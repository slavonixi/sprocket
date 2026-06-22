from django.urls import path, include
from . import logs

urlpatterns = [
    path("", include("api.urls")),
]           