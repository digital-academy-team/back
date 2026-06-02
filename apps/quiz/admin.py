from django.contrib import admin

from apps.course.models.units import CourseUnit
from apps.quiz.models import Quiz, Questions, QuizResult, Variant

# Register your models here.


admin.site.register(Quiz)
admin.site.register(Questions)
admin.site.register(QuizResult)
admin.site.register(Variant)

