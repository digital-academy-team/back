from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from apps.course.filters import CourseFilter
from apps.course.models.course import Course
from common.serializers.courses.course import CourseDetailSerializer, CourseUserListSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.select_related("category", "created_by").prefetch_related("units", "units__lessons")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CourseFilter
    search_fields = ['title']
    lookup_field = 'slug'


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer

        return CourseUserListSerializer


