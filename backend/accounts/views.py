from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import models
from .models import User, PlatformMessage, UserReport, SkillReport
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserListSerializer,
    UserSerializer, UserDetailSerializer, PlatformMessageSerializer,
    UserReportSerializer, SkillReportSerializer, AdminUserSerializer,
    AdminDashboardSerializer, SwapStatsSerializer, UserActivityReportSerializer
)
from django.views.decorators.csrf import ensure_csrf_cookie
from skills.models import Skill, UserSkill
from swaps.models import SwapRequest, SwapSession, SwapRating

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response({
            'message': 'Registration successful',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login user"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        print(f"Login - User: {user.full_name}, Session ID: {request.session.session_key}")
        print(f"Login - Session data: {dict(request.session)}")
        
        response = Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data
        })
        
       
        
        print(f"Login - Set session cookie: sessionid={request.session.session_key}")
        
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user"""
    logout(request)
    return Response({'message': 'Logout successful'})

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_auth(request):
    """Check if user is authenticated"""
    print(f"Check auth - User: {request.user}, Authenticated: {request.user.is_authenticated}")
    print(f"Check auth - Session ID: {request.session.session_key}")
    print(f"Check auth - Cookies: {dict(request.COOKIES)}")
    print(f"Check auth - Session data: {dict(request.session)}")
    print(f"Check auth - User ID in session: {request.session.get('_auth_user_id')}")
    
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserProfileSerializer(request.user).data
        })
    return Response({'authenticated': False})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """Get current user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update current user profile"""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    """Upload a new avatar image for the current user"""
    if 'avatar' not in request.FILES:
        return Response({'error': 'No avatar file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the uploaded file
    avatar_file = request.FILES['avatar']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if avatar_file.content_type not in allowed_types:
        return Response(
            {'error': 'Invalid file type. Only JPEG, PNG, and GIF are allowed.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (max 5MB)
    if avatar_file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'File too large. Maximum size is 5MB.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Delete old avatar if it exists
    if request.user.avatar:
        request.user.avatar.delete(save=False)
    
    # Save the new avatar
    request.user.avatar = avatar_file
    request.user.save()
    
    return Response({
        'message': 'Avatar uploaded successfully',
        'avatar_url': request.user.avatar.url
    })

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_avatar(request):
    """Delete current user's avatar"""
    if request.user.avatar:
        request.user.avatar.delete()
        request.user.save()
        return Response({'message': 'Avatar deleted successfully'})
    return Response({'error': 'No avatar to delete'}, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    """List all users with search functionality"""
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.exclude(id=self.request.user.id).filter(is_active=True)
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(bio__icontains=search) |
                models.Q(location__icontains=search)
            )
        
        return queryset.order_by('-created_at')

class UserDetailView(generics.RetrieveAPIView):
    """Get detailed user information"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({'message': 'CSRF cookie set'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
    """List all users with search functionality"""
    queryset = User.objects.exclude(id=request.user.id).filter(is_active=True)
    search = request.query_params.get('search', None)
    
    if search:
        queryset = queryset.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(bio__icontains=search) |
            models.Q(location__icontains=search)
        )
    
    serializer = UserListSerializer(queryset.order_by('-created_at'), many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_detail(request, user_id):
    """Get detailed user information"""
    try:
        user = User.objects.get(id=user_id, is_active=True)
        serializer = UserListSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_csrf_token(request):
    """Get CSRF token"""
    return JsonResponse({'message': 'CSRF cookie set'})

class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class AdminDashboardView(generics.GenericAPIView):
    """Admin dashboard with statistics and overview"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Basic statistics
        total_users = User.objects.count()
        total_swaps = SwapRequest.objects.count()
        total_reports = UserReport.objects.count()
        total_skill_reports = SkillReport.objects.count()
        pending_reports = UserReport.objects.filter(status='pending').count()
        pending_skill_reports = SkillReport.objects.filter(status='pending').count()
        banned_users = User.objects.filter(is_banned=True).count()
        active_messages = PlatformMessage.objects.filter(is_active=True).count()
        
        # Recent activity
        recent_users = User.objects.order_by('-created_at')[:5].values(
            'id', 'username', 'first_name', 'last_name', 'created_at'
        )
        recent_swaps = SwapRequest.objects.order_by('-created_at')[:5].values(
            'id', 'from_user__first_name', 'from_user__last_name',
            'to_user__first_name', 'to_user__last_name', 'status', 'created_at'
        )
        recent_reports = UserReport.objects.order_by('-created_at')[:5].values(
            'id', 'reporter__first_name', 'reporter__last_name',
            'reported_user__first_name', 'reported_user__last_name', 'status', 'created_at'
        )
        
        # User growth data (last 30 days)
        user_growth = []
        for i in range(30):
            date = timezone.now() - timedelta(days=i)
            count = User.objects.filter(created_at__date=date.date()).count()
            user_growth.append({'date': date.date().isoformat(), 'count': count})
        user_growth.reverse()
        
        # Swap statistics
        swap_stats = {
            'pending': SwapRequest.objects.filter(status='pending').count(),
            'accepted': SwapRequest.objects.filter(status='accepted').count(),
            'completed': SwapRequest.objects.filter(status='completed').count(),
            'cancelled': SwapRequest.objects.filter(status='cancelled').count(),
            'rejected': SwapRequest.objects.filter(status='rejected').count(),
        }
        
        # Report statistics
        report_stats = {
            'pending': UserReport.objects.filter(status='pending').count(),
            'investigating': UserReport.objects.filter(status='investigating').count(),
            'resolved': UserReport.objects.filter(status='resolved').count(),
            'dismissed': UserReport.objects.filter(status='dismissed').count(),
        }
        
        data = {
            'total_users': total_users,
            'total_swaps': total_swaps,
            'total_reports': total_reports,
            'total_skill_reports': total_skill_reports,
            'pending_reports': pending_reports,
            'pending_skill_reports': pending_skill_reports,
            'banned_users': banned_users,
            'active_messages': active_messages,
            'recent_users': list(recent_users),
            'recent_swaps': list(recent_swaps),
            'recent_reports': list(recent_reports),
            'user_growth': user_growth,
            'swap_stats': swap_stats,
            'report_stats': report_stats,
        }
        
        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data)

class AdminUserListView(generics.ListAPIView):
    """List all users for admin management"""
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by('-created_at')

class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    """Get and update user details for admin"""
    permission_classes = [IsAdminUser]
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()

class AdminBanUserView(generics.GenericAPIView):
    """Ban or unban a user"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            is_banned = request.data.get('is_banned', False)
            ban_reason = request.data.get('ban_reason', '')
            
            user.is_banned = is_banned
            if is_banned:
                user.ban_reason = ban_reason
                user.ban_date = timezone.now()
                user.banned_by = request.user
            else:
                user.ban_reason = ''
                user.ban_date = None
                user.banned_by = None
            
            user.save()
            
            return Response({
                'message': f'User {"banned" if is_banned else "unbanned"} successfully',
                'user': AdminUserSerializer(user).data
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class PlatformMessageListView(generics.ListCreateAPIView):
    """List and create platform messages"""
    permission_classes = [IsAdminUser]
    serializer_class = PlatformMessageSerializer
    queryset = PlatformMessage.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PlatformMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, and delete platform messages"""
    permission_classes = [IsAdminUser]
    serializer_class = PlatformMessageSerializer
    queryset = PlatformMessage.objects.all()

class UserReportListView(generics.ListAPIView):
    """List user reports for admin review"""
    permission_classes = [IsAdminUser]
    serializer_class = UserReportSerializer
    queryset = UserReport.objects.all().order_by('-created_at')

class UserReportDetailView(generics.RetrieveUpdateAPIView):
    """Get and update user report details"""
    permission_classes = [IsAdminUser]
    serializer_class = UserReportSerializer
    queryset = UserReport.objects.all()
    
    def perform_update(self, serializer):
        if serializer.validated_data.get('status') in ['resolved', 'dismissed']:
            serializer.save(resolved_by=self.request.user, resolved_at=timezone.now())
        else:
            serializer.save()

class SkillReportListView(generics.ListAPIView):
    """List skill reports for admin review"""
    permission_classes = [IsAdminUser]
    serializer_class = SkillReportSerializer
    queryset = SkillReport.objects.all().order_by('-created_at')

class SkillReportDetailView(generics.RetrieveUpdateAPIView):
    """Get and update skill report details"""
    permission_classes = [IsAdminUser]
    serializer_class = SkillReportSerializer
    queryset = SkillReport.objects.all()
    
    def perform_update(self, serializer):
        if serializer.validated_data.get('status') in ['approved', 'rejected', 'skill_removed']:
            serializer.save(resolved_by=self.request.user, resolved_at=timezone.now())
        else:
            serializer.save()

class SwapStatsView(generics.GenericAPIView):
    """Get detailed swap statistics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Basic stats
        total_swaps = SwapRequest.objects.count()
        pending_swaps = SwapRequest.objects.filter(status='pending').count()
        accepted_swaps = SwapRequest.objects.filter(status='accepted').count()
        completed_swaps = SwapRequest.objects.filter(status='completed').count()
        cancelled_swaps = SwapRequest.objects.filter(status='cancelled').count()
        rejected_swaps = SwapRequest.objects.filter(status='rejected').count()
        
        # Time-based stats
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        year_ago = now - timedelta(days=365)
        
        swaps_this_week = SwapRequest.objects.filter(created_at__gte=week_ago).count()
        swaps_this_month = SwapRequest.objects.filter(created_at__gte=month_ago).count()
        swaps_this_year = SwapRequest.objects.filter(created_at__gte=year_ago).count()
        
        # Average rating
        average_rating = SwapRating.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
        
        # Top skills
        top_offered_skills = Skill.objects.filter(
            offered_in_swaps__isnull=False
        ).annotate(
            count=Count('offered_in_swaps')
        ).order_by('-count')[:10].values('name', 'count')
        
        top_wanted_skills = Skill.objects.filter(
            wanted_in_swaps__isnull=False
        ).annotate(
            count=Count('wanted_in_swaps')
        ).order_by('-count')[:10].values('name', 'count')
        
        data = {
            'total_swaps': total_swaps,
            'pending_swaps': pending_swaps,
            'accepted_swaps': accepted_swaps,
            'completed_swaps': completed_swaps,
            'cancelled_swaps': cancelled_swaps,
            'rejected_swaps': rejected_swaps,
            'swaps_this_week': swaps_this_week,
            'swaps_this_month': swaps_this_month,
            'swaps_this_year': swaps_this_year,
            'average_rating': round(average_rating, 2),
            'top_offered_skills': list(top_offered_skills),
            'top_wanted_skills': list(top_wanted_skills),
        }
        
        serializer = SwapStatsSerializer(data)
        return Response(serializer.data)

class DownloadUserActivityReportView(generics.GenericAPIView):
    """Download user activity report as CSV"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_activity_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User ID', 'Username', 'Email', 'Full Name', 'Join Date', 'Last Login',
            'Total Swaps', 'Completed Swaps', 'Average Rating', 'Reports Received',
            'Reports Made', 'Is Banned', 'Ban Reason'
        ])
        
        users = User.objects.all()
        for user in users:
            total_swaps = SwapRequest.objects.filter(
                Q(from_user=user) | Q(to_user=user)
            ).count()
            
            completed_swaps = SwapRequest.objects.filter(
                Q(from_user=user) | Q(to_user=user),
                status='completed'
            ).count()
            
            # Calculate average rating from swap ratings
            user_ratings = SwapRating.objects.filter(
                swap_session__swap_request__from_user=user
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
            
            reports_received = UserReport.objects.filter(reported_user=user).count()
            reports_made = UserReport.objects.filter(reporter=user).count()
            
            writer.writerow([
                user.id, user.username, user.email, user.full_name,
                user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                total_swaps, completed_swaps, round(user_ratings, 2),
                reports_received, reports_made, user.is_banned, user.ban_reason or ''
            ])
        
        return response

class DownloadSwapReportView(generics.GenericAPIView):
    """Download swap activity report as CSV"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="swap_activity_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Swap ID', 'From User', 'To User', 'Skill Offered', 'Skill Wanted',
            'Status', 'Duration', 'Preferred Time', 'Created At', 'Updated At'
        ])
        
        swaps = SwapRequest.objects.all().select_related('from_user', 'to_user', 'skill_offered', 'skill_wanted')
        for swap in swaps:
            writer.writerow([
                swap.id, swap.from_user.full_name, swap.to_user.full_name,
                swap.skill_offered.name, swap.skill_wanted.name, swap.status,
                swap.duration, swap.preferred_time,
                swap.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                swap.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

class DownloadReportLogView(generics.GenericAPIView):
    """Download report logs as CSV"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Report ID', 'Type', 'Reporter', 'Reported User/Skill', 'Report Type',
            'Description', 'Status', 'Admin Notes', 'Resolved By', 'Resolved At',
            'Created At'
        ])
        
        # User reports
        user_reports = UserReport.objects.all().select_related('reporter', 'reported_user', 'resolved_by')
        for report in user_reports:
            writer.writerow([
                f'UR-{report.id}', 'User Report', report.reporter.full_name,
                report.reported_user.full_name, report.report_type,
                report.description[:100], report.status, report.admin_notes[:100],
                report.resolved_by.full_name if report.resolved_by else '',
                report.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if report.resolved_at else '',
                report.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Skill reports
        skill_reports = SkillReport.objects.all().select_related('reporter', 'skill', 'resolved_by')
        for report in skill_reports:
            writer.writerow([
                f'SR-{report.id}', 'Skill Report', report.reporter.full_name,
                report.skill.name, report.report_type,
                report.description[:100], report.status, report.admin_notes[:100],
                report.resolved_by.full_name if report.resolved_by else '',
                report.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if report.resolved_at else '',
                report.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

class AdminSkillManagementView(generics.GenericAPIView):
    """Admin view for managing skills and rejecting inappropriate descriptions"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get all skills with user counts and report counts"""
        from skills.models import Skill, UserSkill
        
        skills = Skill.objects.annotate(
            user_count=Count('userskills'),
            report_count=Count('skillreports')
        ).order_by('-user_count')
        
        # Get skills with reports
        reported_skills = Skill.objects.filter(
            skillreports__isnull=False
        ).distinct().annotate(
            report_count=Count('skillreports'),
            pending_reports=Count('skillreports', filter=Q(skillreports__status='pending'))
        )
        
        data = {
            'total_skills': skills.count(),
            'skills': [
                {
                    'id': skill.id,
                    'name': skill.name,
                    'description': skill.description,
                    'user_count': skill.user_count,
                    'report_count': skill.report_count,
                    'created_at': skill.created_at
                }
                for skill in skills
            ],
            'reported_skills': [
                {
                    'id': skill.id,
                    'name': skill.name,
                    'description': skill.description,
                    'total_reports': skill.report_count,
                    'pending_reports': skill.pending_reports,
                    'reports': [
                        {
                            'id': report.id,
                            'reporter': report.reporter.full_name,
                            'report_type': report.report_type,
                            'description': report.description,
                            'status': report.status,
                            'created_at': report.created_at
                        }
                        for report in skill.skillreports.all()[:5]  # Show last 5 reports
                    ]
                }
                for skill in reported_skills
            ]
        }
        
        return Response(data)
    
    def post(self, request):
        """Reject or approve a skill description"""
        skill_id = request.data.get('skill_id')
        action = request.data.get('action')  # 'reject' or 'approve'
        reason = request.data.get('reason', '')
        
        try:
            skill = Skill.objects.get(id=skill_id)
            
            if action == 'reject':
                # Mark all pending reports as resolved
                SkillReport.objects.filter(
                    skill=skill, 
                    status='pending'
                ).update(
                    status='skill_removed',
                    admin_notes=f"Skill rejected: {reason}",
                    resolved_by=request.user,
                    resolved_at=timezone.now()
                )
                
                # Optionally, you could also remove the skill or mark it as inactive
                # skill.is_active = False
                # skill.save()
                
                return Response({
                    'message': f'Skill "{skill.name}" rejected successfully',
                    'reason': reason
                })
            
            elif action == 'approve':
                # Mark all pending reports as resolved
                SkillReport.objects.filter(
                    skill=skill, 
                    status='pending'
                ).update(
                    status='approved',
                    admin_notes=f"Skill approved: {reason}",
                    resolved_by=request.user,
                    resolved_at=timezone.now()
                )
                
                return Response({
                    'message': f'Skill "{skill.name}" approved successfully',
                    'reason': reason
                })
            
            else:
                return Response(
                    {'error': 'Invalid action. Use "reject" or "approve".'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Skill.DoesNotExist:
            return Response(
                {'error': 'Skill not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AdminSwapMonitoringView(generics.GenericAPIView):
    """Admin view for monitoring all swaps"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get all swaps with filtering options"""
        status_filter = request.query_params.get('status', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        swaps = SwapRequest.objects.select_related(
            'from_user', 'to_user', 'skill_offered', 'skill_wanted'
        ).order_by('-created_at')
        
        if status_filter:
            swaps = swaps.filter(status=status_filter)
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_swaps = swaps[start:end]
        
        # Get swap statistics
        total_swaps = swaps.count()
        status_counts = {
            'pending': swaps.filter(status='pending').count(),
            'accepted': swaps.filter(status='accepted').count(),
            'completed': swaps.filter(status='completed').count(),
            'cancelled': swaps.filter(status='cancelled').count(),
            'rejected': swaps.filter(status='rejected').count(),
        }
        
        data = {
            'swaps': [
                {
                    'id': swap.id,
                    'from_user': {
                        'id': swap.from_user.id,
                        'name': swap.from_user.full_name,
                        'email': swap.from_user.email
                    },
                    'to_user': {
                        'id': swap.to_user.id,
                        'name': swap.to_user.full_name,
                        'email': swap.to_user.email
                    },
                    'skill_offered': swap.skill_offered.name,
                    'skill_wanted': swap.skill_wanted.name,
                    'status': swap.status,
                    'duration': swap.duration,
                    'preferred_time': swap.preferred_time,
                    'created_at': swap.created_at,
                    'updated_at': swap.updated_at,
                    'message': swap.message
                }
                for swap in paginated_swaps
            ],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total_swaps,
                'total_pages': (total_swaps + page_size - 1) // page_size
            },
            'statistics': status_counts
        }
        
        return Response(data)
    
    def post(self, request):
        """Admin can cancel or modify a swap"""
        swap_id = request.data.get('swap_id')
        action = request.data.get('action')  # 'cancel' or 'modify'
        reason = request.data.get('reason', '')
        
        try:
            swap = SwapRequest.objects.get(id=swap_id)
            
            if action == 'cancel':
                if swap.status in ['pending', 'accepted']:
                    swap.status = 'cancelled'
                    swap.save()
                    
                    # Create a platform message to notify users
                    PlatformMessage.objects.create(
                        title=f"Swap Cancelled by Admin",
                        content=f"Your swap (ID: {swap.id}) has been cancelled by an administrator. Reason: {reason}",
                        message_type='notification',
                        created_by=request.user,
                        is_active=True
                    )
                    
                    return Response({
                        'message': f'Swap {swap.id} cancelled successfully',
                        'reason': reason
                    })
                else:
                    return Response(
                        {'error': 'Cannot cancel swap in current status'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            elif action == 'modify':
                # Allow admin to modify swap details
                new_status = request.data.get('new_status')
                new_duration = request.data.get('new_duration')
                new_preferred_time = request.data.get('new_preferred_time')
                
                if new_status:
                    swap.status = new_status
                if new_duration:
                    swap.duration = new_duration
                if new_preferred_time:
                    swap.preferred_time = new_preferred_time
                
                swap.save()
                
                return Response({
                    'message': f'Swap {swap.id} modified successfully',
                    'changes': {
                        'status': new_status,
                        'duration': new_duration,
                        'preferred_time': new_preferred_time
                    }
                })
            
            else:
                return Response(
                    {'error': 'Invalid action. Use "cancel" or "modify".'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except SwapRequest.DoesNotExist:
            return Response(
                {'error': 'Swap not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AdminEnhancedReportsView(generics.GenericAPIView):
    """Enhanced admin reports with more detailed analytics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get comprehensive platform analytics"""
        report_type = request.query_params.get('type', 'overview')
        
        if report_type == 'overview':
            return self._get_overview_report()
        elif report_type == 'user_activity':
            return self._get_user_activity_report()
        elif report_type == 'swap_analytics':
            return self._get_swap_analytics_report()
        elif report_type == 'moderation':
            return self._get_moderation_report()
        else:
            return Response(
                {'error': 'Invalid report type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_overview_report(self):
        """Get platform overview statistics"""
        now = timezone.now()
        month_ago = now - timedelta(days=30)
        
        # User statistics
        total_users = User.objects.count()
        new_users_this_month = User.objects.filter(created_at__gte=month_ago).count()
        active_users = User.objects.filter(last_login__gte=month_ago).count()
        banned_users = User.objects.filter(is_banned=True).count()
        
        # Swap statistics
        total_swaps = SwapRequest.objects.count()
        swaps_this_month = SwapRequest.objects.filter(created_at__gte=month_ago).count()
        completed_swaps = SwapRequest.objects.filter(status='completed').count()
        completion_rate = (completed_swaps / total_swaps * 100) if total_swaps > 0 else 0
        
        # Report statistics
        total_reports = UserReport.objects.count() + SkillReport.objects.count()
        pending_reports = UserReport.objects.filter(status='pending').count() + SkillReport.objects.filter(status='pending').count()
        
        # Rating statistics
        avg_rating = SwapRating.objects.aggregate(avg=Avg('rating'))['avg'] or 0
        
        data = {
            'platform_overview': {
                'total_users': total_users,
                'new_users_this_month': new_users_this_month,
                'active_users': active_users,
                'banned_users': banned_users,
                'total_swaps': total_swaps,
                'swaps_this_month': swaps_this_month,
                'completed_swaps': completed_swaps,
                'completion_rate': round(completion_rate, 2),
                'total_reports': total_reports,
                'pending_reports': pending_reports,
                'average_rating': round(avg_rating, 2)
            }
        }
        
        return Response(data)
    
    def _get_user_activity_report(self):
        """Get detailed user activity report"""
        # Top active users
        top_active_users = User.objects.annotate(
            swap_count=Count('sent_requests') + Count('received_requests'),
            rating_count=Count('received_ratings')
        ).order_by('-swap_count')[:10]
        
        # User growth over time
        user_growth = []
        for i in range(12):  # Last 12 months
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            new_users = User.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            user_growth.append({
                'month': month_start.strftime('%Y-%m'),
                'new_users': new_users
            })
        
        data = {
            'top_active_users': [
                {
                    'id': user.id,
                    'name': user.full_name,
                    'email': user.email,
                    'swap_count': user.swap_count,
                    'rating_count': user.rating_count,
                    'join_date': user.created_at
                }
                for user in top_active_users
            ],
            'user_growth': user_growth
        }
        
        return Response(data)
    
    def _get_swap_analytics_report(self):
        """Get detailed swap analytics"""
        # Swap success rates by skill
        from skills.models import Skill
        
        skill_success_rates = []
        for skill in Skill.objects.all():
            total_swaps = SwapRequest.objects.filter(
                Q(skill_offered=skill) | Q(skill_wanted=skill)
            ).count()
            
            completed_swaps = SwapRequest.objects.filter(
                Q(skill_offered=skill) | Q(skill_wanted=skill),
                status='completed'
            ).count()
            
            success_rate = (completed_swaps / total_swaps * 100) if total_swaps > 0 else 0
            
            skill_success_rates.append({
                'skill_name': skill.name,
                'total_swaps': total_swaps,
                'completed_swaps': completed_swaps,
                'success_rate': round(success_rate, 2)
            })
        
        # Swap trends over time
        swap_trends = []
        for i in range(12):  # Last 12 months
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            total_swaps = SwapRequest.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            completed_swaps = SwapRequest.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end,
                status='completed'
            ).count()
            
            swap_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'total_swaps': total_swaps,
                'completed_swaps': completed_swaps
            })
        
        data = {
            'skill_success_rates': skill_success_rates,
            'swap_trends': swap_trends
        }
        
        return Response(data)
    
    def _get_moderation_report(self):
        """Get moderation activity report"""
        # Recent moderation actions
        recent_bans = User.objects.filter(
            is_banned=True,
            ban_date__gte=timezone.now() - timedelta(days=30)
        ).order_by('-ban_date')[:10]
        
        recent_reports = list(UserReport.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:10]) + list(SkillReport.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:10])
        
        # Sort by creation date
        recent_reports.sort(key=lambda x: x.created_at, reverse=True)
        
        data = {
            'recent_bans': [
                {
                    'user_id': user.id,
                    'user_name': user.full_name,
                    'ban_reason': user.ban_reason,
                    'ban_date': user.ban_date,
                    'banned_by': user.banned_by.full_name if user.banned_by else 'System'
                }
                for user in recent_bans
            ],
            'recent_reports': [
                {
                    'id': report.id,
                    'type': 'User Report' if hasattr(report, 'reported_user') else 'Skill Report',
                    'reporter': report.reporter.full_name,
                    'reported_item': report.reported_user.full_name if hasattr(report, 'reported_user') else report.skill.name,
                    'report_type': report.report_type,
                    'status': report.status,
                    'created_at': report.created_at
                }
                for report in recent_reports[:10]
            ]
        }
        
        return Response(data)

class DownloadEnhancedReportView(generics.GenericAPIView):
    """Download enhanced reports as CSV"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        report_type = request.query_params.get('type', 'user_activity')
        
        if report_type == 'user_activity':
            return self._download_user_activity_report()
        elif report_type == 'swap_analytics':
            return self._download_swap_analytics_report()
        elif report_type == 'moderation_log':
            return self._download_moderation_log_report()
        else:
            return Response(
                {'error': 'Invalid report type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _download_user_activity_report(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="enhanced_user_activity_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User ID', 'Username', 'Email', 'Full Name', 'Join Date', 'Last Login',
            'Total Swaps', 'Completed Swaps', 'Cancelled Swaps', 'Average Rating',
            'Reports Received', 'Reports Made', 'Is Banned', 'Ban Reason',
            'Total Skills Offered', 'Total Skills Wanted'
        ])
        
        users = User.objects.all()
        for user in users:
            total_swaps = SwapRequest.objects.filter(
                Q(from_user=user) | Q(to_user=user)
            ).count()
            
            completed_swaps = SwapRequest.objects.filter(
                Q(from_user=user) | Q(to_user=user),
                status='completed'
            ).count()
            
            cancelled_swaps = SwapRequest.objects.filter(
                Q(from_user=user) | Q(to_user=user),
                status='cancelled'
            ).count()
            
            user_ratings = SwapRating.objects.filter(
                swap_session__swap_request__from_user=user
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
            
            reports_received = UserReport.objects.filter(reported_user=user).count()
            reports_made = UserReport.objects.filter(reporter=user).count()
            
            from skills.models import UserSkill
            skills_offered = UserSkill.objects.filter(user=user, skill_type='offered').count()
            skills_wanted = UserSkill.objects.filter(user=user, skill_type='wanted').count()
            
            writer.writerow([
                user.id, user.username, user.email, user.full_name,
                user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                total_swaps, completed_swaps, cancelled_swaps, round(user_ratings, 2),
                reports_received, reports_made, user.is_banned, user.ban_reason or '',
                skills_offered, skills_wanted
            ])
        
        return response
    
    def _download_swap_analytics_report(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="swap_analytics_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Swap ID', 'From User', 'To User', 'Skill Offered', 'Skill Wanted',
            'Status', 'Duration', 'Preferred Time', 'Created At', 'Updated At',
            'Completion Date', 'Rating Given', 'Rating Received'
        ])
        
        swaps = SwapRequest.objects.all().select_related(
            'from_user', 'to_user', 'skill_offered', 'skill_wanted'
        )
        
        for swap in swaps:
            # Get completion date and ratings
            completion_date = ''
            rating_given = ''
            rating_received = ''
            
            if swap.status == 'completed':
                try:
                    swap_session = SwapSession.objects.get(swap_request=swap)
                    completion_date = swap_session.completed_at.strftime('%Y-%m-%d %H:%M:%S') if swap_session.completed_at else ''
                    
                    # Get ratings
                    ratings = SwapRating.objects.filter(swap_session=swap_session)
                    for rating in ratings:
                        if rating.rater == swap.from_user:
                            rating_given = rating.rating
                        else:
                            rating_received = rating.rating
                except SwapSession.DoesNotExist:
                    pass
            
            writer.writerow([
                swap.id, swap.from_user.full_name, swap.to_user.full_name,
                swap.skill_offered.name, swap.skill_wanted.name, swap.status,
                swap.duration, swap.preferred_time,
                swap.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                swap.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                completion_date, rating_given, rating_received
            ])
        
        return response
    
    def _download_moderation_log_report(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="moderation_log_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Action Type', 'Target', 'Action By', 'Action Date', 'Reason/Notes',
            'Status', 'Related Reports'
        ])
        
        # User bans
        banned_users = User.objects.filter(is_banned=True)
        for user in banned_users:
            writer.writerow([
                'User Ban', user.full_name, user.banned_by.full_name if user.banned_by else 'System',
                user.ban_date.strftime('%Y-%m-%d %H:%M:%S') if user.ban_date else '',
                user.ban_reason or '', 'Active', ''
            ])
        
        # Report resolutions
        resolved_reports = list(UserReport.objects.filter(
            status__in=['resolved', 'dismissed']
        )) + list(SkillReport.objects.filter(
            status__in=['approved', 'rejected', 'skill_removed']
        ))
        
        for report in resolved_reports:
            report_type = 'User Report' if hasattr(report, 'reported_user') else 'Skill Report'
            target = report.reported_user.full_name if hasattr(report, 'reported_user') else report.skill.name
            
            writer.writerow([
                f'{report_type} Resolution', target,
                report.resolved_by.full_name if report.resolved_by else 'System',
                report.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if report.resolved_at else '',
                report.admin_notes or '', report.status, report.id
            ])
        
        return response

