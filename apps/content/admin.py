from django.contrib import admin

from .models import (ContentArticle, ContentArticleComment, ContentBookmark,
                     ContentCategory, ContentLearningPath, ContentQuiz,
                     ContentQuizAttempt, ContentReport, ContentSeries,
                     ContentTag, UserLearningProgress)


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "type",
        "is_active",
        "order",
        "article_count")
    list_filter = ("type", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    def article_count(self, obj):
        return obj.articles.filter(status="PUBLISHED").count()

    article_count.short_description = "Published Articles"


@admin.register(ContentTag)
class ContentTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "usage_count", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ContentArticle)
class ContentArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "content_type",
        "status",
        "author",
        "views",
        "likes",
        "published_at",
    )
    list_filter = (
        "content_type",
        "status",
        "is_featured",
        "is_educational",
        "is_premium",
        "language",
    )
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = (
        "views",
        "unique_views",
        "likes",
        "dislikes",
        "shares",
        "bookmarks",
        "created_at",
        "updated_at",
    )
    filter_horizontal = ("categories", "tags", "related_articles")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "slug",
                    "content",
                    "summary",
                    "content_type",
                    "status",
                )
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "audience",
                    "language",
                    "categories",
                    "tags",
                    "related_articles",
                )
            },
        ),
        (
            "Media",
            {"fields": ("featured_image", "banner_image",
                        "video_url", "audio_url")},
        ),
        (
            "Metadata",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                    "canonical_url",
                    "schema_markup",
                )
            },
        ),
        (
            "Feature Flags",
            {
                "fields": (
                    "is_featured",
                    "is_educational",
                    "is_premium",
                    "is_verified",
                    "allow_comments",
                    "allow_sharing",
                )
            },
        ),
        (
            "Stats",
            {
                "fields": (
                    "views",
                    "unique_views",
                    "likes",
                    "dislikes",
                    "shares",
                    "comments_count",
                    "bookmarks",
                    "reading_time",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "published_at",
                    "reviewed_at",
                    "reviewed_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(ContentArticleComment)
class ContentArticleCommentAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "author",
        "content_preview",
        "is_approved",
        "is_flagged",
        "created_at",
    )
    list_filter = ("is_approved", "is_flagged")
    search_fields = ("content", "author__username")
    actions = ["approve_comments"]

    def content_preview(self, obj):
        return obj.content[:50] + \
            "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    approve_comments.short_description = "Approve selected comments"


@admin.register(ContentBookmark)
class ContentBookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    search_fields = ("user__username", "article__title")


@admin.register(ContentSeries)
class ContentSeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "is_featured")
    list_filter = ("is_active", "is_featured")
    search_fields = ("title", "description")
    filter_horizontal = ("articles",)


@admin.register(ContentQuiz)
class ContentQuizAdmin(admin.ModelAdmin):
    list_display = ("article", "title", "passing_score", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "article__title")


@admin.register(ContentQuizAttempt)
class ContentQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("quiz", "user", "score", "passed", "completed_at")
    list_filter = ("passed",)
    search_fields = ("user__username", "quiz__title")


@admin.register(ContentLearningPath)
class ContentLearningPathAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "is_active", "is_featured")
    list_filter = ("difficulty", "is_active", "is_featured")
    search_fields = ("title", "description")
    filter_horizontal = ("articles", "required_articles")


@admin.register(UserLearningProgress)
class UserLearningProgressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "learning_path",
        "status",
        "progress",
        "last_activity")
    list_filter = ("status",)
    search_fields = ("user__username", "learning_path__title")
    filter_horizontal = ("completed_articles",)


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = (
        "reporter",
        "article",
        "report_type",
        "status",
        "created_at")
    list_filter = ("report_type", "status")
    search_fields = ("reporter__username", "article__title", "description")
