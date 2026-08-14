from rest_framework import generics

from apps.accounts.permissions import IsEducationOfficer

from .models import School, Term
from .serializers import SchoolSerializer, TermSerializer


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