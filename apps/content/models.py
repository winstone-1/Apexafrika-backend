from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class ContentCategory(models.Model):
    """Content categories for organization"""
    
    class CategoryType(models.TextChoices):
        GAME = 'GAME', 'Game'
        SKILL = 'SKILL', 'Skill Development'
        STRATEGY = 'STRATEGY', 'Strategy'
        COMMUNITY = 'COMMUNITY', 'Community'
        TOURNAMENT = 'TOURNAMENT', 'Tournament'
        NEWS = 'NEWS', 'News'
        INTERVIEW = 'INTERVIEW', 'Interview'
        TUTORIAL = 'TUTORIAL', 'Tutorial'
        REVIEW = 'REVIEW', 'Review'
        OPINION = 'OPINION', 'Opinion'
        HEALTH = 'HEALTH', 'Health & Wellness'
        TECH = 'TECH', 'Technology'
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=CategoryType.choices, default=CategoryType.GAME)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='content_icons/', blank=True, null=True)
    color = models.CharField(max_length=7, default='#FFB300')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Content Categories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('content:category-detail', kwargs={'slug': self.slug})

class ContentTag(models.Model):
    """Tags for content articles"""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-usage_count']),
        ]
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

class ContentArticle(models.Model):
    """Main content article model"""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING = 'PENDING', 'Pending Review'
        REVIEWED = 'REVIEWED', 'Reviewed'
        PUBLISHED = 'PUBLISHED', 'Published'
        ARCHIVED = 'ARCHIVED', 'Archived'
        DELETED = 'DELETED', 'Deleted'
    
    class ContentType(models.TextChoices):
        ARTICLE = 'ARTICLE', 'Article'
        GUIDE = 'GUIDE', 'Guide'
        TUTORIAL = 'TUTORIAL', 'Tutorial'
        NEWS = 'NEWS', 'News'
        INTERVIEW = 'INTERVIEW', 'Interview'
        REVIEW = 'REVIEW', 'Game Review'
        OPINION = 'OPINION', 'Opinion'
        CASE_STUDY = 'CASE_STUDY', 'Case Study'
        WHITEPAPER = 'WHITEPAPER', 'Whitepaper'
        VIDEO = 'VIDEO', 'Video'
        PODCAST = 'PODCAST', 'Podcast'
        INFOGRAPHIC = 'INFOGRAPHIC', 'Infographic'
    
    class Audience(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'
        ALL = 'ALL', 'All Levels'
    
    class Language(models.TextChoices):
        ENGLISH = 'en', 'English'
        SWAHILI = 'sw', 'Swahili'
        FRENCH = 'fr', 'French'
        ARABIC = 'ar', 'Arabic'
    
    # Core fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    summary = models.TextField(max_length=500, help_text="Brief summary for previews")
    
    # Classification
    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.ARTICLE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.ALL)
    language = models.CharField(max_length=10, choices=Language.choices, default=Language.ENGLISH)
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_articles')
    categories = models.ManyToManyField(ContentCategory, related_name='articles')
    tags = models.ManyToManyField(ContentTag, related_name='articles')
    related_articles = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_to')
    
    # Media
    featured_image = models.ImageField(upload_to='content_images/featured/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='content_images/banners/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo URL")
    audio_url = models.URLField(blank=True, null=True, help_text="Podcast audio URL")
    
    # Metadata
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True, max_length=160)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    
    # Stats
    views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    bookmarks = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=5, help_text="Estimated reading time in minutes")
    
    # Feature flags
    is_featured = models.BooleanField(default=False)
    is_educational = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text="Requires subscription to view")
    is_verified = models.BooleanField(default=False, help_text="Verified by experts")
    allow_comments = models.BooleanField(default=True)
    allow_sharing = models.BooleanField(default=True)
    
    # SEO
    canonical_url = models.URLField(blank=True, null=True)
    schema_markup = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['content_type']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['language']),
            models.Index(fields=['slug']),
            models.Index(fields=['-views']),
            models.Index(fields=['-likes']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('content:article-detail', kwargs={'slug': self.slug})
    
    def publish(self):
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=['status', 'published_at'])
    
    def increment_views(self, unique_visitor=False):
        self.views += 1
        if unique_visitor:
            self.unique_views += 1
        self.save(update_fields=['views', 'unique_views'])
    
    def increment_likes(self):
        self.likes += 1
        self.save(update_fields=['likes'])
    
    def increment_shares(self):
        self.shares += 1
        self.save(update_fields=['shares'])
    
    def add_bookmark(self):
        self.bookmarks += 1
        self.save(update_fields=['bookmarks'])
    
    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

class ContentArticleView(models.Model):
    """Track individual article views per user/visitor"""
    
    article = models.ForeignKey(ContentArticle, on_delete=models.CASCADE, related_name='article_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='content_views')
    visitor_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    referer = models.URLField(blank=True, null=True)
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")
    scroll_depth = models.IntegerField(default=0, help_text="Percentage of page scrolled")
    
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['article', '-viewed_at']),
            models.Index(fields=['user']),
            models.Index(fields=['visitor_id']),
        ]
    
    def __str__(self):
        return f"{self.article.title} - {self.viewed_at}"

class ContentArticleComment(models.Model):
    """Comments on content articles"""
    
    article = models.ForeignKey(ContentArticle, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    
    is_approved = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, null=True)
    
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', '-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.author.username} - {self.content[:50]}..."
    
    def approve(self):
        self.is_approved = True
        self.save(update_fields=['is_approved'])
    
    def flag(self, reason=None):
        self.is_flagged = True
        self.flag_reason = reason
        self.save(update_fields=['is_flagged', 'flag_reason'])

class ContentBookmark(models.Model):
    """User bookmarks for articles"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_bookmarks')
    article = models.ForeignKey(ContentArticle, on_delete=models.CASCADE, related_name='bookmarked_by')
    note = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'article']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title}"

class ContentSeries(models.Model):
    """Series of related articles"""
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='content_series/', blank=True, null=True)
    
    articles = models.ManyToManyField(ContentArticle, related_name='series')
    order = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_series')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name_plural = 'Content Series'
    
    def __str__(self):
        return self.title

class ContentQuiz(models.Model):
    """Quizzes for educational content"""
    
    article = models.ForeignKey(ContentArticle, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    questions = models.JSONField()
    passing_score = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.article.title} - Quiz"

class ContentQuizAttempt(models.Model):
    """User quiz attempts"""
    
    quiz = models.ForeignKey(ContentQuiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField()
    answers = models.JSONField()
    passed = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['quiz', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"

class ContentLearningPath(models.Model):
    """Learning paths for users"""
    
    class Difficulty(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'
        EXPERT = 'EXPERT', 'Expert'
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    image = models.ImageField(upload_to='learning_paths/', blank=True, null=True)
    
    articles = models.ManyToManyField(ContentArticle, related_name='learning_paths')
    required_articles = models.ManyToManyField(ContentArticle, related_name='required_for_paths')
    order = models.IntegerField(default=0)
    
    estimated_completion_time = models.DurationField(help_text="Estimated time to complete")
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_learning_paths')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.difficulty}"

class UserLearningProgress(models.Model):
    """Track user progress through learning paths"""
    
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CERTIFIED = 'CERTIFIED', 'Certified'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_progress')
    learning_path = models.ForeignKey(ContentLearningPath, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    completed_articles = models.ManyToManyField(ContentArticle, related_name='completed_by_users')
    
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    certified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'learning_path']
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.learning_path.title} - {self.progress}%"
    
    def update_progress(self):
        total_articles = self.learning_path.articles.count()
        completed = self.completed_articles.count()
        if total_articles > 0:
            self.progress = (completed / total_articles) * 100
            if self.progress >= 100 and self.status != self.Status.COMPLETED:
                self.status = self.Status.COMPLETED
                self.completed_at = timezone.now()
                if self.learning_path.is_certified:
                    self.status = self.Status.CERTIFIED
                    self.certified_at = timezone.now()
            self.save()

class ContentReport(models.Model):
    """Reports for content moderation"""
    
    class ReportType(models.TextChoices):
        INAPPROPRIATE = 'INAPPROPRIATE', 'Inappropriate Content'
        SPAM = 'SPAM', 'Spam'
        MISINFORMATION = 'MISINFORMATION', 'Misinformation'
        COPYRIGHT = 'COPYRIGHT', 'Copyright Infringement'
        HARASSMENT = 'HARASSMENT', 'Harassment'
        OTHER = 'OTHER', 'Other'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        REVIEWING = 'REVIEWING', 'Reviewing'
        RESOLVED = 'RESOLVED', 'Resolved'
        REJECTED = 'REJECTED', 'Rejected'
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_reports')
    article = models.ForeignKey(ContentArticle, on_delete=models.CASCADE, related_name='reports')
    comment = models.ForeignKey(ContentArticleComment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    review_notes = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.reporter.username} reported {self.article.title}"
