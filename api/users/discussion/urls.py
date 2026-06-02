from django.urls import path

from api.users.discussion.views import DiscussionPostListCreateView


urlpatterns = [
    path('<uuid:lesson_id>/posts/', DiscussionPostListCreateView.as_view(), name='discussion-posts'),
]
