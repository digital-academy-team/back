from django.contrib import admin

from apps.course.models.category import Category
from apps.course.models.course import Course
from apps.course.models.lessons import Lessons
from apps.course.models.student import CourseStudent
from apps.course.models.units import CourseUnit
from apps.course.models.assignment_submission import AssignmentSubmission, AssignmentSubmissionFile
from apps.course.models.student_activity import DiscussionPost, ExerciseSubmission

# Register your models here.


admin.site.register(Course)
admin.site.register(CourseStudent)
admin.site.register(Lessons)

admin.site.register(Category)

admin.site.register(CourseUnit)
admin.site.register(AssignmentSubmission)
admin.site.register(AssignmentSubmissionFile)
admin.site.register(DiscussionPost)
admin.site.register(ExerciseSubmission)