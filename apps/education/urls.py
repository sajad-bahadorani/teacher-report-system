from django.urls import path

from .views import (
    SchoolListCreateView,
    SchoolUpdateView,
    TermListCreateView,
    TermUpdateView,
    ClassroomListCreateView,
    ClassroomUpdateView,
    TeacherAssignmentListCreateView,
    TeacherAssignmentUpdateView,
    MyClassroomListView,
)


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
    path(
        "terms/",
        TermListCreateView.as_view(),
        name="term-list-create",
    ),
    path(
        "terms/<int:pk>/",
        TermUpdateView.as_view(),
        name="term-update",
    ),

    path(
        "classrooms/",
        ClassroomListCreateView.as_view(),
        name="classroom-list-create",
    ),
    path(
        "classrooms/<int:pk>/",
        ClassroomUpdateView.as_view(),
        name="classroom-update",
    ),
    path(
        "teacher-assignments/",
        TeacherAssignmentListCreateView.as_view(),
        name="teacher-assignment-list-create",
    ),
    path(
        "teacher-assignments/<int:pk>/",
        TeacherAssignmentUpdateView.as_view(),
        name="teacher-assignment-update",
    ),
    path(
        "my-classrooms/",
        MyClassroomListView.as_view(),
        name="my-classrooms",
    ),
]