from rest_framework import viewsets
from rest_framework.decorators import action

from apps.course.models.course import Course
from common.serializers.courses.course import CourseDetailSerializer, CourseUserListSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer

        return CourseUserListSerializer




    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        courses = super().get_queryset().filter(user=self.request.user)
