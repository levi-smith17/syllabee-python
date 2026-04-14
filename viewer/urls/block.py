from django.urls import path
from viewer.views.block import *


app_name = 'block'
urlpatterns = [
    path('', BlockIndexView.as_view(), name='index'),
    path('content/', BlockContentView.as_view(), name='content'),
    path('print/', BlockPrintView.as_view(), name='print'),
    path('toc/', BlockTocView.as_view(), name='toc'),
]
