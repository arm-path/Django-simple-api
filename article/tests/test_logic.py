from django.test import TestCase
from django.contrib.auth.models import User

from article.models import Category, Article, ArticleRelation


class GetRatingTestCase(TestCase):
    def setUp(self):
        self.category_1 = Category.objects.create(title='Category-1')
        self.category_2 = Category.objects.create(title='Category-2')
        self.user_1 = User.objects.create(username='user-1')
        self.user_2 = User.objects.create(username='user-2')
        self.article_1 = Article.objects.create(title='article-1', category=self.category_1,
                                                description='Article-description-1', owner=self.user_1)
        self.article_relation_1 = ArticleRelation.objects.create(article=self.article_1, user=self.user_1, rating=3)
        self.article_relation_2 = ArticleRelation.objects.create(article=self.article_1, user=self.user_2, rating=5)

    def test_file_logic(self):
        """ Тестирование метода  get_rating"""
        self.assertEqual(4.0, self.article_1.rating)
        self.article_relation_1.rating = 4
        self.article_relation_1.save()
        self.assertEqual(4.50, self.article_1.rating)
