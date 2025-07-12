from django.urls import path
from . import views

urlpatterns = [
    path('requests/', views.SwapRequestListCreateView.as_view(), name='swap_requests'),
    path('requests/received/', views.ReceivedRequestsView.as_view(), name='received_requests'),
    path('requests/<int:pk>/status/', views.update_request_status, name='update_request_status'),
]
