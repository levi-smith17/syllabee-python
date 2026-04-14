from django.urls import include, path
from core.views import *


app_name = 'core'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('copyright_version/', CopyrightVersionView.as_view(), name='copyright_version'),
]
