from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Skill, UserSkill
from .serializers import SkillSerializer, UserSkillSerializer, UserSkillCreateSerializer

class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserSkillListView(generics.ListCreateAPIView):
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSkillCreateSerializer
        return UserSkillSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(f"UserSkillListView - User: {request.user.full_name}")
        print(f"UserSkillListView - Skills found: {len(serializer.data)}")
        print(f"UserSkillListView - Data: {serializer.data}")
        return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_user_skill(request, pk):
    try:
        user_skill = UserSkill.objects.get(pk=pk, user=request.user)
        user_skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except UserSkill.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_skills_by_type(request, skill_type):
    if skill_type not in ['offered', 'wanted']:
        return Response({'error': 'Invalid skill type'}, status=status.HTTP_400_BAD_REQUEST)
    
    skills = UserSkill.objects.filter(user=request.user, skill_type=skill_type)
    serializer = UserSkillSerializer(skills, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def discover_skills(request):
    """
    Discover skills that other users have - shows skills with user information
    """
    # Get all UserSkills except the current user's
    user_skills = UserSkill.objects.exclude(user=request.user).select_related('user', 'skill')
    
    # Apply filters
    search = request.query_params.get('search', '')
    category = request.query_params.get('category', '')
    skill_type = request.query_params.get('skill_type', '')
    
    if search:
        user_skills = user_skills.filter(
            Q(skill__name__icontains=search) | 
            Q(skill__description__icontains=search) |
            Q(user__full_name__icontains=search)
        )
    
    if category and category != 'all':
        user_skills = user_skills.filter(skill__category=category)
    
    if skill_type:
        user_skills = user_skills.filter(skill_type=skill_type)
    
    # Group by skill and include user information
    skills_data = {}
    for user_skill in user_skills:
        skill_id = user_skill.skill.id
        if skill_id not in skills_data:
            skills_data[skill_id] = {
                'id': user_skill.skill.id,
                'name': user_skill.skill.name,
                'category': user_skill.skill.category,
                'description': user_skill.skill.description,
                'users': []
            }
        
        skills_data[skill_id]['users'].append({
            'user_id': user_skill.user.id,
            'user_name': user_skill.user.full_name,
            'skill_type': user_skill.skill_type,
            'proficiency_level': user_skill.proficiency_level,
            'created_at': user_skill.created_at
        })
    
    # Convert to list and add user count
    result = []
    for skill_data in skills_data.values():
        skill_data['user_count'] = len(skill_data['users'])
        result.append(skill_data)
    
    # Sort by user count (most popular first)
    result.sort(key=lambda x: x['user_count'], reverse=True)
    
    return Response(result)
