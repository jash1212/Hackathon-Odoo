from django.urls import path
from . import views

urlpatterns = [
    path('', views.SkillListView.as_view(), name='skill_list'),
    path('discover/', views.discover_skills, name='discover_skills'),
    path('user-skills/', views.UserSkillListView.as_view(), name='user_skills'),
    path('user-skills/<int:pk>/delete/', views.delete_user_skill, name='delete_user_skill'),
    path('user-skills/<str:skill_type>/', views.user_skills_by_type, name='user_skills_by_type'),
]
