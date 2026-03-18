from django.contrib import admin

from apps.course.models.category import Category
from apps.course.models.course import Course
from apps.course.models.lessons import Lessons
from apps.course.models.student import CourseStudent
from apps.course.models.units import CourseUnit

# Register your models here.


admin.site.register(Course)
admin.site.register(CourseStudent)
admin.site.register(Lessons)

admin.site.register(Category)

admin.site.register(CourseUnit)