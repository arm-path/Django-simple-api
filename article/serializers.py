from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Category, Article, ArticleRelation


class CategorySerializer(ModelSerializer):
    """ Сериализация модели Category """

    class Meta:
        model = Category
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ArticleSerializer(ModelSerializer):
    """ Сериализация модели Article """

    owner = serializers.CharField(source='owner.username', read_only=True)
    readers = UserSerializer(many=True, read_only=True)
    count_like_annotate = serializers.IntegerField(read_only=True)


    class Meta:
        model = Article
        fields = (
            'id', 'title', 'category', 'description', 'date_of_publication', 'owner',
            'count_like_annotate',  'rating', 'readers'
        )


class ArticleRelationSerializer(ModelSerializer):
    """ Сериализация модели ArticleRelation """

    class Meta:
        model = ArticleRelation
        fields = ('article', 'like', 'to_favorites', 'rating')
