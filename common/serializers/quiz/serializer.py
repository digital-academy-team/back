from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from apps.quiz.models.questions import Questions
from apps.quiz.models.quiz import Quiz
from apps.quiz.models.variants import Variant
from common.serializers.questions.serializer import QuestionCreateSerializer, QuestionListSerializer


class QuizAnswerItemSerializer(serializers.Serializer):
    question = serializers.UUIDField()
    variant = serializers.UUIDField()


class QuizSubmitSerializer(serializers.Serializer):
    answers = QuizAnswerItemSerializer(many=True)



class QuizListSerializer(ModelSerializer):
    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
                  "id",
                  "title",
                  "description",
                  "is_finished",
                  "due_at",
                  "questions_count"
                  ]


class QuizDetailSerializer(ModelSerializer):

    questions = QuestionListSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
                  "id",
                  "lesson",
                  "title",
                  "description",
                  "questions",
                  "is_finished",
                  "due_at"
                  ]



class QuizCreateSerializer(ModelSerializer):
    questions = QuestionCreateSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = ["lesson", "title", "description", "questions"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")


        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            variants_data = question_data.pop("variants")
            question = Questions.objects.create(quiz=quiz, **question_data)
            for variant_data in variants_data:
                Variant.objects.create(question=question, **variant_data)

        return quiz




class QuizUpdateSerializer(ModelSerializer):
    questions = QuestionCreateSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = ["lesson", "title", "description", "questions"]

    def update(self, instance, validated_data):

        # --- Update Quiz fields ---
        for attr, value in validated_data.items():
            if attr != "questions":
                setattr(instance, attr, value)
        instance.save()

        # --- Nested Questions & Variants ---
        questions_data = validated_data.get("questions", None)
        if questions_data is not None:
            existing_q_ids = [q.id for q in instance.questions.all()]
            incoming_q_ids = []

            for question_data in questions_data:
                variants_data = question_data.pop("variants", [])
                q_id = question_data.get("id", None)

                if q_id and q_id in existing_q_ids:
                    question = Questions.objects.get(id=q_id, quiz=instance)
                    for attr, value in question_data.items():
                        setattr(question, attr, value)
                    question.save()
                else:
                    question = Questions.objects.create(quiz=instance, **question_data)
                incoming_q_ids.append(question.id)

                # Variants update/create/delete
                existing_v_ids = [v.id for v in question.variants.all()]
                incoming_v_ids = []

                for variant_data in variants_data:
                    v_id = variant_data.get("id", None)
                    if v_id and v_id in existing_v_ids:
                        variant = Variant.objects.get(id=v_id, question=question)
                        for attr, value in variant_data.items():
                            setattr(variant, attr, value)
                        variant.save()
                    else:
                        variant = Variant.objects.create(question=question, **variant_data)
                    incoming_v_ids.append(variant.id)

                # Delete removed variants
                for variant in question.variants.all():
                    if variant.id not in incoming_v_ids:
                        variant.delete()

            # Delete removed questions
            for question in instance.questions.all():
                if question.id not in incoming_q_ids:
                    for variant in question.variants.all():
                        variant.delete()
                    question.delete()

        return instance