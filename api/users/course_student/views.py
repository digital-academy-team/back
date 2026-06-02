from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.course.models.student import CourseStudent, ProgressStatus
from common.serializers.course_student.serializer import CourseStudentDetailSerializer, CourseStudentSerializer
from common.utils.generate_certificate import generate_certificate


def _get_full_name(user) -> str:

    name = (user.get_full_name() or "").strip()
    return name if name else user.username


class CourseStudentViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CourseStudent.objects.select_related('user', 'course', 'course__created_by')
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'post', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseStudentDetailSerializer
        return CourseStudentSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='certificate')
    def certificate(self, request, pk=None):
        course_student = self.get_object()

        if course_student.status != ProgressStatus.COMPLETED:
            return Response(
                {"message": "You have not finished yet!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if course_student.certificate_pdf:
            return Response(
                {"message": "Certificate already exists!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pdf_bytes = generate_certificate(
            student_name=_get_full_name(request.user),
            course_name=course_student.course.title,
            instructor_name=_get_full_name(course_student.course.created_by),
            completion_date=course_student.updated_at.strftime("%d %B %Y"),
            organization_name="Digital Academy",
            certificate_id=str(course_student.id),
        )

        filename = f"certificate_{course_student.id}.pdf"
        course_student.certificate_pdf.save(filename, ContentFile(pdf_bytes), save=True)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
