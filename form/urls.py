from django.urls import path
from .views import formListCreateView, formDetailView

urlpatterns = [
    path('forms/', formListCreateView.as_view(), name='form-list-create'),
    path('forms/<int:pk>/', formDetailView.as_view(), name='form-detail'),
]
