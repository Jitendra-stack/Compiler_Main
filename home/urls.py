from django.urls import path
from home.views import all_polls ,poll_detail

urlpatterns = [
    path("polls/", all_polls, name="all-polls"),
    path("polls/<int:poll_id>/", poll_detail, name="poll-detail"),
]
