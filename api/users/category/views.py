from rest_framework import viewsets

from apps.course.models.category import Category
from common.serializers.category.serializer import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.only("id", "title", "slug")
    serializer_class = CategorySerializer







