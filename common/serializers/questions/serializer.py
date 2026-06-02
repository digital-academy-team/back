from rest_framework.serializers import ModelSerializer

from apps.quiz.models.questions import Questions
from common.serializers.variants.serializer import VariantCreateSerializer




class QuestionListSerializer(ModelSerializer):
    variants = VariantCreateSerializer(read_only=True, many=True)

    class Meta:
        model = Questions
        fields = ["id", "question_text", "points", "variants"]


class QuestionCreateSerializer(ModelSerializer):
    variants = VariantCreateSerializer(many=True, required=True)

    class Meta:
        model = Questions
        fields = ["question_text", "points", "variants"]


