from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.course.models.student import CourseStudent
from common.serializers.course_student.serializer import CourseStudentDetailSerializer, CourseStudentSerializer


class CourseStudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStudent.objects.select_related('user', 'course')
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseStudentDetailSerializer

        return CourseStudentSerializer



    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)



