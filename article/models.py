from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """ Модель категорий """
    title = models.CharField(max_length=154, unique=True)

    def __str__(self):
        return f'Категория: {self.title}'


class Article(models.Model):
    """ Модель статей """
    title = models.CharField(max_length=154)
    category = models.ForeignKey(Category, models.PROTECT, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    date_of_publication = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, models.SET_NULL, related_name='article_owner', null=True)
    readers = models.ManyToManyField(User, through='ArticleRelation', related_name='article_readers', null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    def __str__(self):
        return f'Статья: {self.title} ; author: {self.owner}'


class ArticleRelation(models.Model):
    """ Модель посредник между моделями User и Article """
    CHOICES_RATING = (
        (1, 'badly'), (2, 'come down'),
        (3, 'fine'),
        (4, 'good'), (5, 'excellent')
    )
    user = models.ForeignKey(User, models.CASCADE)
    article = models.ForeignKey(Article, models.CASCADE)
    like = models.BooleanField(default=False)
    to_favorites = models.BooleanField(default=False)
    rating = models.SmallIntegerField(choices=CHOICES_RATING, blank=True, null=True)

    def __str__(self):
        return f'Пользователь: {self.user.username} Статья: {self.article.title}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_rating = self.rating

    def save(self, *args, **kwargs):
        from article.logic import get_rating

        creating = not self.pk

        super().save(*args, **kwargs)
        new_rating = self.rating

        if self.old_rating != new_rating or creating:
            get_rating(self.article)

