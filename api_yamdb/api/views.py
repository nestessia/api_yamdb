from rest_framework import (viewsets, permissions, status, filters, mixins)
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg
from api.filters import TitleFilter
from django.shortcuts import get_object_or_404

from reviews.models import Title, Category, Genre, Review
from .serializers import (
    TitleReadSerializer, TitleWriteSerializer,
    CategorySerializer, GenreSerializer, ReviewSerializer,
    CommentsSerializer)
from .permissions import SuperUserOrAdmin, OwnerModerAdmin, IsAdminOrReadOnly
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    ProfileSerializer, TokenSerializer,)
from users.users import User


class UserRegistrationView(APIView):
    """Регистрация пользователя."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, create = User.objects.get_or_create(username=username,
                                                  email=email)

        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            'Your Confirmation code',
            user.confirmation_code,
            ['yamdb@mail.com'],
            (email, ),
            fail_silently=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """Получение JWT-токена."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(
                username=serializer.validated_data['username'])
            confirmation_code = user.confirmation_code
        except User.DoesNotExist:
            return Response(
                {'username': 'Такой пользователь не существует'},
                status=status.HTTP_404_NOT_FOUND)
        if (serializer.validated_data['confirmation_code']
           == confirmation_code):
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response(
            {'confirmation_code': 'Код подтвердения неверный!'},
            status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    permission_classes = (SuperUserOrAdmin, )
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    http_method_names = ("get", "post", "patch", "delete")
    pagination_class = PageNumberPagination

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
    )
    def get_user_info(self, request):
        serializer = ProfileSerializer(request.user, data=request.data,
                                       partial=True)
        serializer.is_valid(raise_exception=True)
        if request.method == "PATCH":
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = (OwnerModerAdmin,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', 'slug')
    search_fields = ('name', 'slug')

    def create(self, request, *args, **kwargs):
        slug = request.data.get('slug')
        existing_category = Category.objects.filter(slug=slug).first()
        if existing_category:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error':
                                  'Категория с таким slug уже существует.'})

        return super().create(request, *args, **kwargs)


class GenereaViewSet(ListCreateDestroyViewSet, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', 'slug')
    search_fields = ('name', 'slug')

    def create(self, request, *args, **kwargs):
        slug = request.data.get('slug')
        existing_category = Genre.objects.filter(slug=slug).first()
        if existing_category:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error':
                                  'Категория с таким slug уже существует.'})

        return super().create(request, *args, **kwargs)


class TitlesViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (OwnerModerAdmin,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
