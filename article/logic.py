from django.db.models import Avg

from .models import ArticleRelation


def get_rating(article):
    """ Метод для получения рейтинга """
    rating_article = ArticleRelation.objects.filter(article=article).aggregate(rating_count=Avg('rating')).get(
        'rating_count')
    article.rating = rating_article
    article.save()


