from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    ContentCategory, ContentTag, ContentArticle, ContentArticleView,
    ContentArticleComment, ContentBookmark, ContentSeries,
    ContentQuiz, ContentQuizAttempt, ContentLearningPath,
    UserLearningProgress, ContentReport
)
from .serializers import (
    ContentCategorySerializer, ContentTagSerializer,
    ContentArticleSerializer, ContentArticleDetailSerializer,
    ContentArticleCommentSerializer, ContentBookmarkSerializer,
    ContentSeriesSerializer, ContentQuizSerializer,
    ContentQuizAttemptSerializer, ContentLearningPathSerializer,
    UserLearningProgressSerializer, ContentReportSerializer
)

class ContentCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Content Categories"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ContentCategorySerializer
    queryset = ContentCategory.objects.filter(is_active=True)
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def articles(self, request, slug=None):
        category = self.get_object()
        articles = category.articles.filter(status='PUBLISHED')
        serializer = ContentArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)

class ContentTagViewSet(viewsets.ModelViewSet):
    """ViewSet for Content Tags"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ContentTagSerializer
    queryset = ContentTag.objects.filter(is_active=True)
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def articles(self, request, slug=None):
        tag = self.get_object()
        articles = tag.articles.filter(status='PUBLISHED')
        tag.increment_usage()
        serializer = ContentArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)

class ContentArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for Content Articles"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ContentArticleSerializer
    queryset = ContentArticle.objects.filter(status='PUBLISHED')
    lookup_field = 'slug'
    filterset_fields = ['content_type', 'is_featured', 'is_educational', 'is_premium', 'language', 'audience']
    search_fields = ['title', 'summary', 'content', 'meta_keywords']
    ordering_fields = ['views', 'likes', 'shares', 'created_at', 'published_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Filter by tag
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Filter by series
        series = self.request.query_params.get('series')
        if series:
            queryset = queryset.filter(series__slug=series)
        
        # Featured articles
        if self.request.query_params.get('featured') == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContentArticleDetailSerializer
        return ContentArticleSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views(unique_visitor=True)
        
        # Track view
        visitor_id = request.query_params.get('visitor_id')
        if not visitor_id and not request.user.is_authenticated:
            visitor_id = request.META.get('HTTP_USER_AGENT', '')[:100]
        
        ContentArticleView.objects.create(
            article=instance,
            user=request.user if request.user.is_authenticated else None,
            visitor_id=visitor_id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            referer=request.META.get('HTTP_REFERER', '')
        )
        
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, slug=None):
        article = self.get_object()
        article.increment_likes()
        return Response({'likes': article.likes})
    
    @action(detail=True, methods=['post'])
    def share(self, request, slug=None):
        article = self.get_object()
        article.increment_shares()
        return Response({'shares': article.shares})
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, slug=None):
        article = self.get_object()
        
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        bookmark, created = ContentBookmark.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if created:
            article.add_bookmark()
            return Response({'message': 'Bookmarked'}, status=status.HTTP_201_CREATED)
        else:
            bookmark.delete()
            article.bookmarks -= 1
            article.save(update_fields=['bookmarks'])
            return Response({'message': 'Bookmark removed'})
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending articles"""
        days = int(request.query_params.get('days', 7))
        time_threshold = timezone.now() - timezone.timedelta(days=days)
        
        articles = ContentArticle.objects.filter(
            status='PUBLISHED',
            published_at__gte=time_threshold
        ).order_by('-views', '-likes', '-shares')[:20]
        
        serializer = ContentArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured articles"""
        articles = ContentArticle.objects.filter(
            status='PUBLISHED',
            is_featured=True
        ).order_by('-published_at')[:10]
        
        serializer = ContentArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular articles by views"""
        articles = ContentArticle.objects.filter(
            status='PUBLISHED'
        ).order_by('-views', '-likes')[:20]
        
        serializer = ContentArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)

class ContentArticleCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Article Comments"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContentArticleCommentSerializer
    
    def get_queryset(self):
        return ContentArticleComment.objects.filter(
            author=self.request.user,
            is_approved=True
        )
    
    def perform_create(self, serializer):
        article_slug = self.request.data.get('article_slug')
        article = get_object_or_404(ContentArticle, slug=article_slug)
        
        serializer.save(
            author=self.request.user,
            article=article,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        article.comments_count += 1
        article.save(update_fields=['comments_count'])
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        comment.likes += 1
        comment.save(update_fields=['likes'])
        return Response({'likes': comment.likes})
    
    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        comment = self.get_object()
        comment.dislikes += 1
        comment.save(update_fields=['dislikes'])
        return Response({'dislikes': comment.dislikes})
    
    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        comment = self.get_object()
        reason = request.data.get('reason')
        comment.flag(reason)
        return Response({'message': 'Comment flagged for review'})

class ContentBookmarkViewSet(viewsets.ModelViewSet):
    """ViewSet for User Bookmarks"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContentBookmarkSerializer
    
    def get_queryset(self):
        return ContentBookmark.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        article_slug = self.request.data.get('article_slug')
        article = get_object_or_404(ContentArticle, slug=article_slug)
        serializer.save(user=self.request.user, article=article)

class ContentSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Content Series"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ContentSeriesSerializer
    queryset = ContentSeries.objects.filter(is_active=True)
    lookup_field = 'slug'

class ContentQuizViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Quizzes"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ContentQuizSerializer
    queryset = ContentQuiz.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def attempt(self, request, pk=None):
        quiz = self.get_object()
        answers = request.data.get('answers')
        
        if not answers:
            return Response(
                {'error': 'Answers are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Calculate score
        correct = 0
        for question in quiz.questions:
            user_answer = answers.get(str(question.get('id')))
            if user_answer == question.get('correct_answer'):
                correct += 1
        
        score = int((correct / len(quiz.questions)) * 100) if quiz.questions else 0
        passed = score >= quiz.passing_score
        
        attempt = ContentQuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            score=score,
            answers=answers,
            passed=passed,
            completed_at=timezone.now()
        )
        
        serializer = ContentQuizAttemptSerializer(attempt)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_attempts(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        attempts = ContentQuizAttempt.objects.filter(user=request.user)
        serializer = ContentQuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)

class ContentLearningPathViewSet(viewsets.ModelViewSet):
    """ViewSet for Learning Paths"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ContentLearningPathSerializer
    queryset = ContentLearningPath.objects.filter(is_active=True)
    lookup_field = 'slug'
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, slug=None):
        path = self.get_object()
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        progress, created = UserLearningProgress.objects.get_or_create(
            user=request.user,
            learning_path=path
        )
        if created:
            progress.status = 'IN_PROGRESS'
            progress.save()
            return Response({'message': 'Enrolled successfully'})
        return Response({'message': 'Already enrolled'})
    
    @action(detail=True, methods=['post'])
    def complete_article(self, request, slug=None):
        path = self.get_object()
        article_slug = request.data.get('article_slug')
        
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        article = get_object_or_404(ContentArticle, slug=article_slug)
        
        progress = get_object_or_404(UserLearningProgress, user=request.user, learning_path=path)
        progress.completed_articles.add(article)
        progress.update_progress()
        
        return Response({
            'progress': progress.progress,
            'status': progress.status,
            'completed': progress.completed_articles.count(),
            'total': path.articles.count()
        })

class UserLearningProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for User Learning Progress"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserLearningProgressSerializer
    
    def get_queryset(self):
        return UserLearningProgress.objects.filter(user=self.request.user)

class ContentReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Content Reports"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContentReportSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ContentReport.objects.all()
        return ContentReport.objects.filter(reporter=self.request.user)
    
    def perform_create(self, serializer):
        article_slug = self.request.data.get('article_slug')
        article = get_object_or_404(ContentArticle, slug=article_slug)
        serializer.save(reporter=self.request.user, article=article)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        report = self.get_object()
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can resolve reports'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        action_taken = request.data.get('action_taken')
        report.status = 'RESOLVED'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        if action_taken:
            report.action_taken = action_taken
        report.save()
        
        return Response({'message': 'Report resolved'})
