# `from rest_framework import serializers
#
# from apps.certificate.models import Certificate
#
#
#
# class CertificateSerializer(serializers.ModelSerializer):
#
#     course_name = serializers.CharField(source="course.title", read_only=True)
#     user_first_name = serializers.CharField(source="user.first_name", read_only=True)
#
#     class Meta:
#         model = Certificate
#         fields = ["course_name", "user_first_name", "certificate"]
#
#
# class CertificateCreateSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Certificate
#         fields = ["course"]