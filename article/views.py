from django.shortcuts import render
from django.db.models import Count, Case, When, Avg
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Article, ArticleRelation
from .permissions import IsAuthenticatedOrReadOnlyModify, IsAuthenticatedReadOnlyModify
from .serializers import CategorySerializer, ArticleSerializer, ArticleRelationSerializer


class ArticleViewSet(ModelViewSet):
    """ Представление данных Article """
    queryset = Article.objects.all().annotate(
        count_like_annotate=Count(Case(When(articlerelation__like=True, then=1)))).select_related(
        'owner').prefetch_related('readers').order_by('id')
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    """ Фильтрация, поиск и сортировка """
    filter_fields = ['category', 'category__title', 'date_of_publication', 'owner', 'owner__username']
    search_fields = ['title']
    ordering_fields = ['title', 'date_of_publication', 'category__title']
    """ Ограничение прав доступа и действий над объектами """
    permission_classes = [IsAuthenticatedOrReadOnlyModify]

    def perform_create(self, serializer):
        """ Переопределение метода класса  CreateModelMixin """
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class CategoryViewSet(ModelViewSet):
    """ Представление данных Category """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    """ Фильтрация, поиск и сортировка """
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['title']
    search_fields = ['title']
    """ Ограничение прав доступа и действий над объектами """
    permission_classes = [IsAuthenticatedReadOnlyModify]


class ArticleRelationViewSet(UpdateModelMixin, GenericViewSet):
    """ Представление данных ArticleRelation """
    queryset = ArticleRelation.objects.all()
    serializer_class = ArticleRelationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'article'

    def get_object(self):
        """ Получение объекта """
        obj, _ = ArticleRelation.objects.get_or_create(user=self.request.user, article_id=self.kwargs['article'])
        return obj


def auth_git(request):
    """ Страница авторизации gitHub """
    return render(request, 'auth.html', {})
