from django.urls import path
from .views import UploadOrdersView, UserStatsView

urlpatterns = [
    path('upload/', UploadOrdersView.as_view(), name='upload-orders'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
]