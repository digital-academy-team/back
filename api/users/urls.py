from django.urls import path, include



urlpatterns = [
    path('auth/', include('api.users.auth.urls')),
    path('quiz/', include('api.users.quizzes.urls')),
    path('enrolment/', include('api.users.enrolment.urls')),
    path('courses/', include('api.users.courses.urls')),
    path('category/', include('api.users.category.urls')),
    path('my-courses/', include('api.users.course_student.urls')),
    path('comments/', include('api.users.comment.urls')),
]
