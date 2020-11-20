import json

from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.db.models import Count, When, Case, Avg

from article.models import Category, Article, ArticleRelation
from article.serializers import ArticleSerializer


class TestSerializersAPITestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='test_user_1')
        self.user_2 = User.objects.create(username='test_user_2')
        self.user_3 = User.objects.create(username='test_user_3')
        self.category_1 = Category.objects.create(title='category-1')
        self.category_2 = Category.objects.create(title='category-2')
        self.article_1 = Article.objects.create(title='article-1',
                                                category=self.category_1,
                                                description='article-description-1',
                                                owner=self.user_2)
        self.article_2 = Article.objects.create(title='article-2',
                                                category=self.category_2,
                                                description='article-description-2',
                                                owner=self.user_1)
        self.article_3 = Article.objects.create(title='article-3',
                                                category=self.category_1,
                                                description='article-description-3',
                                                owner=self.user_3)
        ArticleRelation.objects.create(user=self.user_1, article=self.article_1, like=True, rating=3)
        ArticleRelation.objects.create(user=self.user_2, article=self.article_1, like=True, rating=5)
        ArticleRelation.objects.create(user=self.user_3, article=self.article_1, like=True, rating=4)

        ArticleRelation.objects.create(user=self.user_1, article=self.article_2, like=True, rating=5)
        ArticleRelation.objects.create(user=self.user_2, article=self.article_2, like=True, rating=2)
        ArticleRelation.objects.create(user=self.user_3, article=self.article_2, like=False)


    def test_serializers(self):
        data = [
            {
                'id': self.article_1.id,
                'title': 'article-1',
                'category': self.category_1.id,
                'description': 'article-description-1',
                'date_of_publication': str(self.article_1.date_of_publication.strftime("%Y-%m-%d %H:%M:%S")),
                'owner': self.article_1.owner.username,
                'count_like_annotate': 3,
                'rating': '4.00',
                'readers': [
                    {'id': self.user_1.id, 'username': self.user_1.username},
                    {'id': self.user_2.id, 'username': self.user_2.username},
                    {'id': self.user_3.id, 'username': self.user_3.username},
                ]
            },
            {
                'id': self.article_2.id,
                'title': 'article-2',
                'category': self.category_2.id,
                'description': 'article-description-2',
                'date_of_publication': str(self.article_1.date_of_publication.strftime("%Y-%m-%d %H:%M:%S")),
                'owner': self.article_2.owner.username,
                'count_like_annotate': 2,
                'rating': '3.50',
                'readers': [
                    {'id': self.user_1.id, 'username': self.user_1.username},
                    {'id': self.user_2.id, 'username': self.user_2.username},
                    {'id': self.user_3.id, 'username': self.user_3.username},
                ]
            },
            {
                'id': self.article_3.id,
                'title': 'article-3',
                'category': self.category_1.id,
                'description': 'article-description-3',
                'date_of_publication': str(self.article_1.date_of_publication.strftime("%Y-%m-%d %H:%M:%S")),
                'owner': self.article_3.owner.username,
                'count_like_annotate': 0,
                'rating': None,
                'readers': []
            }
        ]

        articles = Article.objects.all().annotate(
            count_like_annotate=Count(Case(When(articlerelation__like=True, then=1))),
            rating_annotate=Avg('articlerelation__rating')).order_by('id')
        serializer_data = ArticleSerializer(articles, many=True).data
        self.assertEqual(data, serializer_data)
