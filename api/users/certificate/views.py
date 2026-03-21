import uuid

from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.certificate.models import Certificate
from apps.course.models.student import CourseStudent, ProgressStatus
from common.serializers.certificates.serializer import CertificateCreateSerializer, CertificateSerializer
from common.utils.generate_certificate import generate_certificate


def _get_full_name(user) -> str:
    """
    get_full_name() bo'sh string qaytarishi mumkin — username fallback.
    Bu 'NoneType has no attribute decode' xatosining sababi.
    """
    name = (user.get_full_name() or "").strip()
    return name if name else user.username


class CertificateViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):

    queryset = Certificate.objects.select_related("user", "course", "course__created_by")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CertificateCreateSerializer
        return CertificateSerializer


    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # ── 1. Kurs tugatilganligini tekshirish ───────────────────────────────
        course_student = CourseStudent.objects.select_related(
            'course', 'course__created_by'
        ).filter(
            course=data['course'],
            user=request.user,
            status=ProgressStatus.COMPLETED,
        ).first()

        if not course_student:
            return Response(
                {"message": "You have not finished yet!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ── 2. Duplicate tekshiruv ────────────────────────────────────────────
        if Certificate.objects.filter(user=request.user, course=data['course']).exists():
            return Response(
                {"message": "Certificate already exists!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── 3. Ma'lumotlarni yig'ish ──────────────────────────────────────────
        student_name = _get_full_name(request.user)
        course_name = course_student.course.title
        instructor_name = _get_full_name(course_student.course.created_by)
        completion_date = course_student.updated_at.strftime("%d %B %Y")

        # ── 4. Certificate obyekt — id (UUID) darhol tayyor ───────────────────
        certificate = Certificate(
            user=request.user,
            course=course_student.course,
        )

        # ── 5. PDF yaratish — certificate.id ni ishlatamiz ───────────────────
        pdf_bytes = generate_certificate(
            student_name=student_name,
            course_name=course_name,
            completion_date=completion_date,
            instructor_name=instructor_name,
            organization_name="Digital Academy",
            certificate_id=str(certificate.id),
        )

        # ── 6. PDF → FileField ga saqlash + DB ga yozish ─────────────────────
        filename = f"certificate_{certificate.id}.pdf"
        certificate.certificate.save(filename, ContentFile(pdf_bytes), save=True)

        # ── 7. PDF ni to'g'ridan yuklab berish ───────────────────────────────
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
