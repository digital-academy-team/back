from django.urls import path, include



urlpatterns = [
    path('courses/', include('api.teachers.courses.urls')),
    path('quiz/', include('api.teachers.quizzes.urls')),
    path('lesson/', include('api.teachers.lessons.urls')),
    path('assignment/', include('api.teachers.assignments.urls')),
]