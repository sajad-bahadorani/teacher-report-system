from rest_framework import generics

from apps.accounts.permissions import IsEducationOfficer, IsTeacher

from .models import School, Term, Classroom, TeacherAssignment
from .serializers import (
    SchoolSerializer,
    TermSerializer,
    ClassroomSerializer,
    TeacherAssignmentSerializer
)


class SchoolListCreateView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsEducationOfficer]


class SchoolUpdateView(generics.UpdateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsEducationOfficer]


class TermListCreateView(generics.ListCreateAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsEducationOfficer]


class TermUpdateView(generics.UpdateAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsEducationOfficer]


class ClassroomListCreateView(generics.ListCreateAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsEducationOfficer]


class ClassroomUpdateView(generics.UpdateAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsEducationOfficer]


class TeacherAssignmentListCreateView(generics.ListCreateAPIView):
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsEducationOfficer]


class TeacherAssignmentUpdateView(generics.UpdateAPIView):
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsEducationOfficer]


class MyClassroomListView(generics.ListAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return Classroom.objects.filter(
            teacher_assignments__teacher=self.request.user
        ).distinct()