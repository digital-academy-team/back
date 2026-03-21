from rest_framework import serializers
from apps.order.models import Order


class OrderListSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Order
        fields = ["course_title", "total_amount", "status"]




class OrderCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["course"]











