from rest_framework.serializers import ModelSerializer

from apps.quiz.models.variants import Variant


class VariantCreateSerializer(ModelSerializer):
    class Meta:
        model = Variant
        fields = ["id", "text", "is_correct"]