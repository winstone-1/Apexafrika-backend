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
    
    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        """Get all achievements for the current user"""
        achievements = self.get_queryset()
        serializer = UserAchievementSerializer(achievements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def equipped(self, request):
        """Get the equipped achievement"""
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
        """Equip an achievement"""
        user_achievement = self.get_object()
        user_achievement.equip()
        return Response({'message': 'Achievement equipped'})
    
    @action(detail=False, methods=['post'])
    def check_unlocks(self, request):
        """Check if any new achievements should be unlocked"""
        user = request.user
        
        # Check all achievements
        achievements = Achievement.objects.filter(is_active=True)
        unlocked_count = 0
        
        for achievement in achievements:
            # Skip if already unlocked
            if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                continue
            
            # Check conditions
            should_unlock = True
            
            # Check match wins
            if achievement.required_wins > 0:
                wins = user.tournaments_won or 0
                if wins < achievement.required_wins:
                    should_unlock = False
            
            # Check total matches
            if achievement.required_matches > 0:
                matches = user.total_matches or 0
                if matches < achievement.required_matches:
                    should_unlock = False
            
            # Check tournaments
            if achievement.required_tournaments > 0:
                tournaments = user.tournaments_participated or 0
                if tournaments < achievement.required_tournaments:
                    should_unlock = False
            
            # Check streak
            if achievement.required_streak > 0:
                # Implement streak check
                pass
            
            if should_unlock:
                UserAchievement.objects.create(user=user, achievement=achievement)
                unlocked_count += 1
        
        return Response({
            'message': f'Unlocked {unlocked_count} new achievements',
            'unlocked': unlocked_count
        })
