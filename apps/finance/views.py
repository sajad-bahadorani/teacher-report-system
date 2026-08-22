from rest_framework import generics

from apps.accounts.permissions import IsFinanceOfficer

from .models import SalaryRate
from .serializers import SalaryRateSerializer


class SalaryRateListCreateView(generics.ListCreateAPIView):
    queryset = SalaryRate.objects.all()
    serializer_class = SalaryRateSerializer
    permission_classes = [IsFinanceOfficer]