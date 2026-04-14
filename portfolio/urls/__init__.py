from django.urls import include, path
from portfolio.views import *


app_name = 'portfolio'
urlpatterns = [
    path('', PortfolioIndexView.as_view(), name='index'),
    path('create/', PortfolioCreateView.as_view(), name='create'),
    path('detail/', PortfolioDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', PortfolioDeleteView.as_view(), name='delete'),
    path('<int:pk>/detail/', PortfolioDetailView.as_view(), name='detail'),
    path('<int:pk>/download/', PortfolioDownloadView.as_view(), name='download'),
    path('<int:pk>/print/', PortfolioPrintView.as_view(), name='print'),
    path('<int:pk>/update/', PortfolioUpdateView.as_view(), name='update'),
    path('toc/', PortfolioTocView.as_view(), name='toc'),
    path('<int:portfolio_id>/review/', include('portfolio.urls.review')),
]
