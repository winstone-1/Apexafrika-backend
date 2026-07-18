from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    class PostType(models.TextChoices):
        TEXT = 'TEXT', 'Text'
        IMAGE = 'IMAGE', 'Image'
        VIDEO = 'VIDEO', 'Video'
        CLIP = 'CLIP', 'Game Clip'
        ANNOUNCEMENT = 'ANNOUNCEMENT', 'Announcement'
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.TEXT)
    
    media_url = models.URLField(blank=True, null=True)
    media_file = models.FileField(upload_to='community_media/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='community_thumbnails/', blank=True, null=True)
    
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    
    is_published = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['tournament']),
        ]
    
    def __str__(self):
        return f"{self.author.username} - {self.content[:50]}..."

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    
    likes_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.username} - {self.content[:30]}..."

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} liked {self.post or self.comment}"
