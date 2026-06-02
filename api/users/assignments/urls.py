from django.urls import path

from api.users.assignments.views import (
    AssignmentMySubmissionView,
    AssignmentSubmitView,
    ExerciseMySubmissionView,
    ExerciseSolutionView,
    ExerciseSubmitView,
)


urlpatterns = [
    path('assignment/<uuid:lesson_id>/submit/', AssignmentSubmitView.as_view(), name='assignment-submit'),
    path('assignment/<uuid:lesson_id>/submission/', AssignmentMySubmissionView.as_view(), name='assignment-my-submission'),
    path('exercise/<uuid:lesson_id>/solution/', ExerciseSolutionView.as_view(), name='exercise-solution'),
    path('exercise/<uuid:lesson_id>/submit/', ExerciseSubmitView.as_view(), name='exercise-submit'),
    path('exercise/<uuid:lesson_id>/submission/', ExerciseMySubmissionView.as_view(), name='exercise-my-submission'),
]
