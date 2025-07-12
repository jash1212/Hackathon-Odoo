from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('check/', views.check_auth, name='check_auth'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('csrf/', views.get_csrf_token, name='csrf'),
    
    # Admin URLs
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/users/<int:user_id>/ban/', views.AdminBanUserView.as_view(), name='admin_ban_user'),
    
    # Platform Messages
    path('admin/messages/', views.PlatformMessageListView.as_view(), name='admin_messages'),
    path('admin/messages/<int:pk>/', views.PlatformMessageDetailView.as_view(), name='admin_message_detail'),
    
    # Reports
    path('admin/reports/users/', views.UserReportListView.as_view(), name='admin_user_reports'),
    path('admin/reports/users/<int:pk>/', views.UserReportDetailView.as_view(), name='admin_user_report_detail'),
    path('admin/reports/skills/', views.SkillReportListView.as_view(), name='admin_skill_reports'),
    path('admin/reports/skills/<int:pk>/', views.SkillReportDetailView.as_view(), name='admin_skill_report_detail'),
    
    # Statistics and Reports
    path('admin/stats/swaps/', views.SwapStatsView.as_view(), name='admin_swap_stats'),
    path('admin/reports/download/users/', views.DownloadUserActivityReportView.as_view(), name='download_user_report'),
    path('admin/reports/download/swaps/', views.DownloadSwapReportView.as_view(), name='download_swap_report'),
    path('admin/reports/download/logs/', views.DownloadReportLogView.as_view(), name='download_report_logs'),
    
    # Enhanced Admin Features
    path('admin/skills/', views.AdminSkillManagementView.as_view(), name='admin_skills'),
    path('admin/swaps/', views.AdminSwapMonitoringView.as_view(), name='admin_swaps'),
    path('admin/reports/enhanced/', views.AdminEnhancedReportsView.as_view(), name='admin_enhanced_reports'),
    path('admin/reports/download/enhanced/', views.DownloadEnhancedReportView.as_view(), name='download_enhanced_reports'),
]
