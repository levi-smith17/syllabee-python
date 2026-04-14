from django.urls import path
from viewer.views.search import *


app_name = 'search'
urlpatterns = [
    path('detail/', SearchDetailView.as_view(), name='detail'),
    path('instructor/', SearchInstructorSearchView.as_view(), name='instructors'),
    path('instructor/<str:pagination>/', SearchInstructorResultsView.as_view(), name='instructor_pagination'),
    path('syllabus/', SearchSyllabusSearchView.as_view(), name='syllabi'),
    path('syllabus/clear/', SearchClearView.as_view(), name='clear'),
    path('syllabus/results/', SearchSyllabusResultsView.as_view(), name='results'),
    path('syllabus/filter/', SearchSyllabusFilterView.as_view(), name='filter'),
    path('syllabus/filter/clear/<str:filter_key>/', SearchSyllabusResultsView.as_view(), name='filter_clear'),
    path('syllabus/<str:pagination>/', SearchSyllabusResultsView.as_view(), name='pagination'),
]
