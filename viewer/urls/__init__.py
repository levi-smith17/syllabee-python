from django.urls import include, path


app_name = 'viewer'
urlpatterns = [
    path('search/', include('viewer.urls.search')),
    path('i/<str:section_hash>/', include('viewer.urls.interactive')),
    path('p/instructor/<str:instructor>/<str:permalink>/', include('viewer.urls.block')),
    path('p/<str:course_code>/<str:section_code>/<str:term_code>/', include('viewer.urls.traditional')),
    path('print/', include('viewer.urls.print')),
]
