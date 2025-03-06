from django.urls import path
from .views import EventListView, EventDetailView, AttendEventView

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("attend/", AttendEventView.as_view(), name="attend-event"),
]
