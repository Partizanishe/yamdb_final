from django.db.models import Avg
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        model = Title

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if not rating:
            return rating
        return round(rating, 1)


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug')

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['view'].kwargs.get('titles_id')

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)
    title = serializers.HiddenField(default=CurrentTitleDefault(), )

    class Meta:
        fields = '__all__'
        model = Review

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                'Оценкой может быть число от 1 до 10.'
            )
        return value

    def validate(self, data):
        if self.context['request'].method == 'POST':
            author = self.context['request'].user
            title = self.context.get('view').kwargs.get('title_id')
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Не более одного комментария для произведения')
            return data
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class SignupSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя \'me\' недоступно')
        return value

    class Meta:
        model = User
        fields = ('username', 'email')


class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'first_name',
                  'last_name', 'bio')


class CheckConfirmationCode(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
