from rest_framework import generics

from apps.accounts.permissions import IsEducationOfficer

from .models import School
from .serializers import SchoolSerializer


class SchoolListCreateView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsEducationOfficer]


class SchoolUpdateView(generics.UpdateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsEducationOfficer]