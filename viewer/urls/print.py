from django.urls import path
from viewer.views.print import *


app_name = 'print'
urlpatterns = [
    path('<str:section_hash>/', PrintIndexView.as_view(), name='index'),
    path('<str:section_hash>/confirm/', PrintConfirmationView.as_view(), name='confirm'),
    path('<str:course_code>/<str:section_code>/<str:term_code>/', PrintIndexView.as_view(), name='index'),
    path('<str:course_code>/<str:section_code>/<str:term_code>/confirm/', PrintConfirmationView.as_view(),
         name='confirm'),
]
