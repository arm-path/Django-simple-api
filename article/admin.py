from django.contrib import admin
from .models import Category, Article, ArticleRelation

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(ArticleRelation)