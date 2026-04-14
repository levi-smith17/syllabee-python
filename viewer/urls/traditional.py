from django.urls import path
from viewer.views.traditional import *


app_name = 'traditional'
urlpatterns = [
    path('', TraditionalIndexView.as_view(), name='syllabus'),
    path('content/', TraditionalContentView.as_view(), name='content'),
    path('toc/', TraditionalTocView.as_view(), name='toc'),
    path('segment/<int:segment_id>/', TraditionalSegmentView.as_view(), name='segment'),
]
