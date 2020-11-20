"""conf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from article.views import CategoryViewSet, ArticleViewSet, ArticleRelationViewSet
from article.views import auth_git

router = SimpleRouter()
router.register('api/article', ArticleViewSet),
router.register('api/category', CategoryViewSet),
router.register('api/relation', ArticleRelationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    url('auth/', auth_git),
    path('__debug__/', include(debug_toolbar.urls)),
]
urlpatterns += router.urls
