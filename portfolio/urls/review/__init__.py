from django.urls import include, path
from portfolio.views.review import *


app_name = 'review'
urlpatterns = [
    path('create/', PortfolioReviewCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', PortfolioReviewDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', PortfolioReviewUpdateView.as_view(), name='update'),
    #path('<int:review_id>/feedback/', include('portfolio.urls.review.feedback'))
]
