import json

from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, When, Case, Avg

from rest_framework import status
from rest_framework.test import APITestCase

from article.models import Category, Article, ArticleRelation
from article.serializers import CategorySerializer, ArticleSerializer, ArticleRelationSerializer


class TestApiArticle(APITestCase):
    def setUp(self):
        self.category_1 = Category.objects.create(title='category-1')
        self.category_2 = Category.objects.create(title='category-2')
        self.category_3 = Category.objects.create(title='category-delete-NO-MODELS.PROTECT')
        self.user_1 = User.objects.create(username='test-1')
        self.user_2 = User.objects.create(username='test-2')
        self.user_3 = User.objects.create(username='test-admin', is_staff=True)
        self.article_1 = Article.objects.create(title='article-1', category=self.category_1,
                                                description='Article-description-1', owner=self.user_1)
        self.article_2 = Article.objects.create(title='article-2', category=self.category_1,
                                                description='Article-description-2', owner=self.user_2)
        self.article_3 = Article.objects.create(title='article-3', category=self.category_2,
                                                description=' ', owner=self.user_2)

    def test_serializer(self):
        """ Тест сериализации данных """
        url = reverse('article-list')
        response = self.client.get(url)
        articles = Article.objects.all().annotate(
            count_like_annotate=Count(Case(When(articlerelation__like=True, then=1)))).order_by('id')
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

        url = reverse('category-list')
        response = self.client.get(url)
        serializer = CategorySerializer([self.category_1, self.category_2, self.category_3], many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_get(self):
        """ Тест получения объекта """
        url = reverse('article-detail', args=(self.article_1.id,))
        response = self.client.get(url)
        article = Article.objects.filter(id__in=[self.article_1.id]).annotate(
            count_like_annotate=Count(Case(When(articlerelation__like=True, then=1))))
        serializer = ArticleSerializer(article[0])
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

        url = reverse('category-detail', args={self.category_1.id})
        response = self.client.get(url)
        serializer = CategorySerializer(self.category_1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_filter(self):
        """ Тест фильтрации """
        url = reverse('article-list')
        response = self.client.get(url, data={'owner__username': self.user_2.username})
        articles = Article.objects.filter(id__in=[self.article_2.id, self.article_3.id]).annotate(
            count_like_annotate=Count(Case(When(articlerelation__like=True, then=1)))).order_by('id')
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_search(self):
        """ Тест поиска """
        url = reverse('article-list')
        response = self.client.get(url, data={'search': 'article-2'})
        articles = Article.objects.filter(id__in=[self.article_2.id, ]).annotate(
            count_like_annotate=Count(Case(When(articlerelation__like=True, then=1)))).order_by('id')
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

        url = reverse('category-list')
        response = self.client.get(url, data={'search': 'category-2'})
        serializer = CategorySerializer([self.category_2], many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_ordering(self):
        """ Тест сортировки """
        url = reverse('article-list')
        response = self.client.get(url, data={'ordering': 'title'})
        articles = Article.objects.all().annotate(
            count_like_annotate=Count(Case(When(articlerelation__like=True, then=1)))).order_by('title')
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

        url = reverse('category-list')
        response = self.client.get(url, data={'ordering': '-title'})
        serializer = CategorySerializer([self.category_3, self.category_2, self.category_1], many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_create(self):
        """ Тест создания объекта """
        self.client.force_login(self.user_2)
        url = reverse('article-list')
        data = {
            "category": 2,
            "title": "article-4",
            "description": "Article description-4",
            "readers": []
        }
        data_json = json.dumps(data)
        response = self.client.post(url, data=data_json, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Article.objects.all().count())
        self.assertEqual(self.user_2, Article.objects.last().owner)

        """ Тестирование 403 FORBIDDEN - Создание категории обычным пользователем """
        url = reverse('category-list')
        data = {
            'title': 'category-3'
        }
        data_json = json.dumps(data)
        response = self.client.post(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Category.objects.all().count())

        """ Тестирование 201 CREATED - Создание категории администратором системы """
        self.client.force_login(self.user_3)
        response = self.client.post(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Category.objects.all().count())

    def test_update(self):
        """ Тест обновления """
        self.client.force_login(self.user_1)
        url = reverse('article-detail', args=(self.article_1.id,))
        data = {
            "category": self.article_1.category.id,
            "title": "Change article title",
            "description": self.article_1.description,
        }
        data_json = json.dumps(data)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.article_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(data['title'], self.article_1.title)

        """ Тестирование 403 FORBIDDEN - Обновление категории обычным пользователем """
        url = reverse('category-detail', args=(self.category_1.id,))
        data = {
            "title": "Change title"
        }
        data_json = json.dumps(data)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        """ Тестирование 201 CREATED - Обновление категории администратором системы """
        self.client.force_login(self.user_3)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.category_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(data['title'], self.category_1.title)

    def test_update_403_FORBIDDEN(self):
        """ Тест изменения чужого объекта """
        self.client.force_login(self.user_2)
        url = reverse('article-detail', args=(self.article_1.id,))
        data = {
            "category": self.article_1.category.id,
            "title": "403 FORBIDDEN",
            "description": self.article_1.description,
        }
        data_json = json.dumps(data)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('article-1', self.article_1.title)

    def test_delete(self):
        """ Тест удаления объекта """
        self.client.force_login(self.user_1)
        url = reverse('article-detail', args=(self.article_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Article.objects.all().count())

        """ Тестирование 403 FORBIDDEN - Удаления категории обычным пользователем """
        url = reverse('category-detail', args=(self.category_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        """ Тестирование 204 NO CONTENT - Удаления категории администратором системы """
        self.client.force_login(self.user_3)
        url = reverse('category-detail', args=(self.category_3.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Category.objects.all().count())

    def test_delete_403_FORBIDDEN(self):
        """ Тест удаления чужого объекта """
        self.client.force_login(self.user_2)
        url = reverse('article-detail', args=(self.article_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Article.objects.all().count())

    def test_update_user_is_staff(self):
        """ Тест обновления чужого объекта администратором """
        self.client.force_login(self.user_3)
        url = reverse('article-detail', args=(self.article_1.id,))
        data = {
            'title': 'change admin article-1',
            'category': self.article_1.category.id,
            'description': self.article_1.description
        }
        data_json = json.dumps(data)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.article_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(data['title'], self.article_1.title)

    def test_delete_user_is_staff(self):
        """ Тест удаления чужого объекта администратором """
        self.client.force_login(self.user_3)
        url = reverse('article-detail', args=(self.article_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Article.objects.all().count())

    def test_get_relation_article_user(self):
        """ Тестирование связи - Лайк"""
        self.client.force_login(self.user_2)
        url = reverse('articlerelation-detail', args=(self.article_1.id,))
        data = {
            'like': True
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        relation = ArticleRelation.objects.get(user=self.user_2, article=self.article_1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.like)

        """ Тестирование связи - Избранное """
        data = {
            'to_favorites': True
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        relation = ArticleRelation.objects.get(user=self.user_2, article=self.article_1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.to_favorites)

    def test_get_relation_article_user_rating(self):
        """ Тестирование проставления рейтинга """
        self.client.force_login(self.user_3)
        url = reverse('articlerelation-detail', args=(self.article_2.id,))
        data = {
            'rating': 4
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        relation = ArticleRelation.objects.get(user=self.user_3, article=self.article_2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(4, relation.rating)

        """ Тестирование проставления рейтинга, для тестирования среднего рейтинга """
        self.client.force_login(self.user_2)
        data = {
            'rating': 5
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        relation = ArticleRelation.objects.get(user=self.user_2, article=self.article_2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, relation.rating)

        """ Тестирование среднего рейтинга """
        url = reverse('article-detail', args=(self.article_2.id,))
        response = self.client.get(url)
        article = Article.objects.filter(id__in=[self.article_2.id, ]).annotate(
            count_like_annotate=Count(Case(When(articlerelation__like=True, then=1))))
        data_article = ArticleSerializer(article[0]).data
        self.assertEqual(data_article, response.data)
        self.assertEqual('4.50', response.data['rating'])
        self.assertEqual('4.50', data_article['rating'])
