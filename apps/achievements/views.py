from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer, UserAchievementSerializer

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = AchievementSerializer
    queryset = Achievement.objects.filter(is_active=True, is_visible=True)
    filterset_fields = ['category', 'tier']
    search_fields = ['name', 'description']

class UserAchievementViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAchievementSerializer
    
    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)
    
    def _check_achievement_conditions(self, user, achievement):
        """Check if a user meets achievement conditions"""
        conditions = []
        
        if achievement.required_wins > 0:
            conditions.append(user.tournaments_won >= achievement.required_wins)
        if achievement.required_matches > 0:
            conditions.append(user.total_matches >= achievement.required_matches)
        if achievement.required_tournaments > 0:
            conditions.append(user.tournaments_participated >= achievement.required_tournaments)
        
        return all(conditions)
    
    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        achievements = self.get_queryset()
        serializer = UserAchievementSerializer(achievements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def equipped(self, request):
        achievement = UserAchievement.objects.filter(
            user=request.user,
            is_equipped=True
        ).first()
        
        if achievement:
            serializer = UserAchievementSerializer(achievement)
            return Response(serializer.data)
        return Response({'message': 'No achievement equipped'})
    
    @action(detail=True, methods=['post'])
    def equip(self, request, pk=None):
        user_achievement = self.get_object()
        user_achievement.equip()
        return Response({'message': 'Achievement equipped'})
    
    @action(detail=False, methods=['post'])
    def check_unlocks(self, request):
        user = request.user
        unlocked_count = 0
        
        for achievement in Achievement.objects.filter(is_active=True):
            if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                continue
            
            if self._check_achievement_conditions(user, achievement):
                UserAchievement.objects.create(user=user, achievement=achievement)
                unlocked_count += 1
        
        return Response({
            'message': f'Unlocked {unlocked_count} new achievements',
            'unlocked': unlocked_count
        })
