from django.db import transaction
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.course.models.student import CourseStudent
from apps.order.models import Order
from common.serializers.order.serializer import OrderCreateSerializer, OrderListSerializer


class EnrolmentViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):

    queryset = Order.objects.select_related('course', 'user')
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderListSerializer


    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            order = serializer.save(user=request.user)

            course_student, created = CourseStudent.objects.get_or_create(
                course=order.course,
                user=order.user,
                defaults={"progress": 0}
            )

        return Response(
            {
                "message": "Successfully Enrolled!",
                "enrolled": created
            },
            status=status.HTTP_201_CREATED
        )





