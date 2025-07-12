from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import SwapRequest
from .serializers import SwapRequestSerializer, SwapRequestCreateSerializer

class SwapRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SwapRequestCreateSerializer
        return SwapRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        
        # Get requests sent by or received by the user
        queryset = SwapRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset

class ReceivedRequestsView(generics.ListAPIView):
    serializer_class = SwapRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        
        queryset = SwapRequest.objects.filter(to_user=user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_request_status(request, pk):
    try:
        swap_request = SwapRequest.objects.get(pk=pk, to_user=request.user)
        new_status = request.data.get('status')
        
        if new_status not in ['accepted', 'rejected']:
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        swap_request.status = new_status
        swap_request.save()
        
        # Update user statistics if accepted
        if new_status == 'accepted':
            swap_request.from_user.completed_swaps += 1
            swap_request.to_user.completed_swaps += 1
            swap_request.from_user.save()
            swap_request.to_user.save()
        
        serializer = SwapRequestSerializer(swap_request)
        return Response(serializer.data)
        
    except SwapRequest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
