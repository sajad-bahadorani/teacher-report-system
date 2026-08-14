from django.urls import path

from .views import SchoolListCreateView, SchoolUpdateView


urlpatterns = [
    path(
        "schools/",
        SchoolListCreateView.as_view(),
        name="school-list-create",
    ),
    path(
        "schools/<int:pk>/",
        SchoolUpdateView.as_view(),
        name="school-update",
    ),
]