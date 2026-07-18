from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            post.likes_count = F('likes_count') + 1
            post.save()
            return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            post.likes_count = F('likes_count') - 1
            post.save()
            return Response({'message': 'Post unliked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        content = request.data.get('content')
        parent_id = request.data.get('parent_id')
        
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent_id=parent_id
        )
        
        post.comments_count = F('comments_count') + 1
        post.save()
        
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, comment=comment)
        
        if created:
            comment.likes_count = F('likes_count') + 1
            comment.save()
            return Response({'message': 'Comment liked'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            comment.likes_count = F('likes_count') - 1
            comment.save()
            return Response({'message': 'Comment unliked'}, status=status.HTTP_200_OK)
