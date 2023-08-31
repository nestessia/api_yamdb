from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, UserRegistrationView, UserViewSet, TokenView,
    CommentViewSet, ReviewViewSet, TitlesViewSet, GenereaViewSet)


router = DefaultRouter()
router.register('users', UserViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')
router.register(r'titles', TitlesViewSet, basename='titles')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenereaViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/auth/signup/', UserRegistrationView.as_view()),
]
