from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Title(models.Model):
    time = [MaxValueValidator(date.today().year)]
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование произведения'
    )
    year = models.IntegerField(verbose_name='Год публикации',
                               validators=time)
    description = models.CharField(max_length=400)
    genre = models.ManyToManyField(
        'Genre',
        blank=True,
        related_name='titles'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return f'{self.name} {self.name}'


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Наименование жанра')
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.IntegerField(validators=[
        MaxValueValidator(10, 'Значение выше максимального порога'),
        MinValueValidator(1, 'Значение ниже минимального порога')
    ])
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    def __str__(self):
        return self.text


class Roles:
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    ]

    bio = models.CharField(
        max_length=1000,
        null=True,
        verbose_name='Users biography'
    )
    confirmation_code = models.CharField(
        max_length=10,
        null=True,
        verbose_name='Confirmation Code'
    )
    role = models.CharField(
        max_length=max(len(role[1]) for role in ROLE_CHOICES),
        default='user',
        choices=ROLE_CHOICES,
        verbose_name='Role'
    )
    email = models.EmailField(max_length=250, unique=True,
                              blank=False, null=False)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator' or self.is_staff

    class Meta:
        ordering = ('role', 'username',)
        db_table = 'users'
