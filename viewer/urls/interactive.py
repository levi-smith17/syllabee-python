from django.urls import path
from viewer.views.interactive import *


app_name = 'interactive'
urlpatterns = [
    path('', InteractiveIndexView.as_view(), name='syllabus'),
    path('end/', InteractiveEndView.as_view(), name='end'),
    path('complete/', InteractiveCompleteView.as_view(), name='complete'),
    path('content/', InteractiveContentView.as_view(), name='content'),
    path('start/<str:view>/', InteractiveStartView.as_view(), name='start'),
    path('toc/<str:view>/', InteractiveTocView.as_view(), name='toc'),
    path('block/<int:pk>/', InteractiveBondView.as_view(extra_context={'clicked': 'current'}), name='block'),
    path('block/<int:pk>/check/', InteractiveBondView.as_view(extra_context={'clicked': 'check'}), name='check'),
    path('block/<int:pk>/next/', InteractiveBondView.as_view(extra_context={'clicked': 'next'}), name='next'),
    path('block/<int:pk>/prev/', InteractiveBondView.as_view(extra_context={'clicked': 'previous'}), name='prev'),
    path('button/<int:pk>/', InteractiveButtonView.as_view(), name='button'),
    path('segment/<int:segment_id>/', InteractiveSegmentView.as_view(), name='segment'),
]
