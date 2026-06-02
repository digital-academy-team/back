from django.urls import path

from api.teachers.assignments.views import (
    AssignmentSubmissionGradeView,
    AssignmentSubmissionListView,
    TutorSubmissionInboxView,
)


urlpatterns = [
    path('submissions/', TutorSubmissionInboxView.as_view(), name='teacher-assignment-inbox'),
    path('<uuid:lesson_id>/submissions/', AssignmentSubmissionListView.as_view(), name='teacher-assignment-submissions'),
    path('submission/<uuid:submission_id>/grade/', AssignmentSubmissionGradeView.as_view(), name='teacher-assignment-grade'),
]
