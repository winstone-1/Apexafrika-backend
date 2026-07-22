from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ContentArticleCommentViewSet, ContentArticleViewSet,
                    ContentBookmarkViewSet, ContentCategoryViewSet,
                    ContentLearningPathViewSet, ContentQuizViewSet,
                    ContentReportViewSet, ContentSeriesViewSet,
                    ContentTagViewSet, UserLearningProgressViewSet)

router = DefaultRouter()
router.register(
    r"categories",
    ContentCategoryViewSet,
    basename="content-category")
router.register(r"tags", ContentTagViewSet, basename="content-tag")
router.register(r"articles", ContentArticleViewSet, basename="content-article")
router.register(
    r"comments",
    ContentArticleCommentViewSet,
    basename="content-comment")
router.register(
    r"bookmarks",
    ContentBookmarkViewSet,
    basename="content-bookmark")
router.register(r"series", ContentSeriesViewSet, basename="content-series")
router.register(r"quizzes", ContentQuizViewSet, basename="content-quiz")
router.register(
    r"learning-paths", ContentLearningPathViewSet, basename="content-learning-path"
)
router.register(
    r"my-learning", UserLearningProgressViewSet, basename="content-learning-progress"
)
router.register(r"reports", ContentReportViewSet, basename="content-report")

app_name = "content"

urlpatterns = [
    path("", include(router.urls)),
]
