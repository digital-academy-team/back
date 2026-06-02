import django_filters
from apps.course.models.course import Course
from apps.course.models.category import Category


class CourseFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.only("title"),
        field_name='category',
    )
    price_min = django_filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='base_price', lookup_expr='lte')

    class Meta:
        model = Course
        fields = ['category', 'price_min', 'price_max']
