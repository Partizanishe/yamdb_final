from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters import CharFilter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Roles, Title, User
from .pagination import UsersPagination
from .permissions import (AdminOrReadOnly, IsAuthorOrReadOnly, IsRoleAdmin,
                          IsRoleModerator)
from .serializers import (CategorySerializer, CheckConfirmationCode,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SignupSerializer, TitleCreateSerializer,
                          TitleSerializer, UserViewSerializer)


class TitleFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='contains')
    category = CharFilter(field_name='category__slug', lookup_expr='exact')
    genre = CharFilter(field_name='genre__slug', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleCreateSerializer


class CreatDestroyListViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreatDestroyListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'


class GenreViewSet(CreatDestroyListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsRoleAdmin | IsRoleModerator | IsAuthorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsRoleAdmin | IsRoleModerator | IsAuthorOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


class Signup(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = default_token_generator.make_token(
            serializer.save(role=Roles.USER)
        )
        send_mail(
            subject='Код подтверждения',
            message=f'{confirmation_code}',
            from_email=settings.EMAIL,
            recipient_list=[serializer.data['email']],
            fail_silently=False
        )
        return Response(data=serializer.data)


class Token(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = CheckConfirmationCode(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': f'{token}'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserViewSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, IsRoleAdmin)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('=username',)
    pagination_class = UsersPagination

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,),
            methods=['get', 'patch'], url_path='me')
    def get_or_update_self(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.user.role == Roles.USER:
            serializer.validated_data['role'] = Roles.USER
        serializer.save()
        return Response(serializer.data)
