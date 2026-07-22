from rest_framework import serializers

from .models import (ContentArticle, ContentArticleComment, ContentBookmark,
                     ContentCategory, ContentLearningPath, ContentQuiz,
                     ContentQuizAttempt, ContentReport, ContentSeries,
                     ContentTag, UserLearningProgress)


class ContentCategorySerializer(serializers.ModelSerializer):
    """Serializer for Content Categories"""

    subcategories = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = ContentCategory
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_subcategories(self, obj):
        return ContentCategorySerializer(
            obj.subcategories.filter(is_active=True), many=True
        ).data

    def get_article_count(self, obj):
        return obj.articles.filter(status="PUBLISHED").count()


class ContentTagSerializer(serializers.ModelSerializer):
    """Serializer for Content Tags"""

    class Meta:
        model = ContentTag
        fields = "__all__"
        read_only_fields = ("usage_count", "created_at", "updated_at")


class ContentArticleCommentSerializer(serializers.ModelSerializer):
    """Serializer for Article Comments"""

    author_details = serializers.StringRelatedField(source="author.username")
    replies = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source="likes", read_only=True)

    class Meta:
        model = ContentArticleComment
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "likes",
            "dislikes",
            "is_approved",
            "is_flagged",
        )

    def get_replies(self, obj):
        if obj.parent is None:
            return ContentArticleCommentSerializer(
                obj.replies.filter(is_approved=True), many=True
            ).data
        return []


class ContentArticleSerializer(serializers.ModelSerializer):
    """Serializer for Content Articles"""

    author_details = serializers.StringRelatedField(source="author.username")
    categories_details = ContentCategorySerializer(
        source="categories", many=True, read_only=True
    )
    tags_details = ContentTagSerializer(
        source="tags", many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = ContentArticle
        fields = "__all__"
        read_only_fields = (
            "views",
            "unique_views",
            "likes",
            "dislikes",
            "shares",
            "comments_count",
            "bookmarks",
            "created_at",
            "updated_at",
            "published_at",
            "reviewed_at",
        )

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ContentBookmark.objects.filter(
                user=request.user, article=obj
            ).exists()
        return False


class ContentArticleDetailSerializer(ContentArticleSerializer):
    """Extended serializer for article detail view"""

    related_articles = serializers.SerializerMethodField()
    series_details = serializers.SerializerMethodField()

    class Meta:
        model = ContentArticle
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "summary",
            "content_type",
            "status",
            "audience",
            "language",
            "author",
            "author_details",
            "categories",
            "categories_details",
            "tags",
            "tags_details",
            "related_articles",
            "featured_image",
            "banner_image",
            "video_url",
            "audio_url",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "views",
            "unique_views",
            "likes",
            "dislikes",
            "shares",
            "comments_count",
            "bookmarks",
            "reading_time",
            "is_featured",
            "is_educational",
            "is_premium",
            "is_verified",
            "allow_comments",
            "allow_sharing",
            "canonical_url",
            "schema_markup",
            "published_at",
            "reviewed_at",
            "reviewed_by",
            "created_at",
            "updated_at",
            "is_bookmarked",
            "series_details",
        ]
        read_only_fields = ContentArticleSerializer.Meta.read_only_fields

    def get_related_articles(self, obj):
        return ContentArticleSerializer(
            obj.related_articles.filter(status="PUBLISHED")[:5],
            many=True,
            context=self.context,
        ).data

    def get_series_details(self, obj):
        series = obj.series.filter(is_active=True).first()
        if series:
            return ContentSeriesSerializer(series).data
        return None


class ContentBookmarkSerializer(serializers.ModelSerializer):
    """Serializer for User Bookmarks"""

    article_details = ContentArticleSerializer(
        source="article", read_only=True)

    class Meta:
        model = ContentBookmark
        fields = "__all__"
        read_only_fields = ("user", "created_at")


class ContentSeriesSerializer(serializers.ModelSerializer):
    """Serializer for Content Series"""

    articles = ContentArticleSerializer(many=True, read_only=True)
    article_count = serializers.IntegerField(
        source="articles.count", read_only=True)

    class Meta:
        model = ContentSeries
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ContentQuizSerializer(serializers.ModelSerializer):
    """Serializer for Quizzes"""

    class Meta:
        model = ContentQuiz
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ContentQuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for Quiz Attempts"""

    quiz_details = ContentQuizSerializer(source="quiz", read_only=True)
    user_details = serializers.StringRelatedField(source="user.username")

    class Meta:
        model = ContentQuizAttempt
        fields = "__all__"
        read_only_fields = ("started_at",)


class ContentLearningPathSerializer(serializers.ModelSerializer):
    """Serializer for Learning Paths"""

    articles = ContentArticleSerializer(many=True, read_only=True)
    article_count = serializers.IntegerField(
        source="articles.count", read_only=True)

    class Meta:
        model = ContentLearningPath
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class UserLearningProgressSerializer(serializers.ModelSerializer):
    """Serializer for User Learning Progress"""

    learning_path_details = ContentLearningPathSerializer(
        source="learning_path", read_only=True
    )
    user_details = serializers.StringRelatedField(source="user.username")
    completed_articles_details = ContentArticleSerializer(
        source="completed_articles", many=True, read_only=True
    )

    class Meta:
        model = UserLearningProgress
        fields = "__all__"
        read_only_fields = (
            "started_at",
            "last_activity",
            "completed_at",
            "certified_at",
        )


class ContentReportSerializer(serializers.ModelSerializer):
    """Serializer for Content Reports"""

    reporter_details = serializers.StringRelatedField(
        source="reporter.username")
    article_details = ContentArticleSerializer(
        source="article", read_only=True)

    class Meta:
        model = ContentReport
        fields = "__all__"
        read_only_fields = ("created_at",)
