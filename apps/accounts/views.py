from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from .permissions import IsTeacher, IsEducationOfficer, IsFinanceOfficer



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        return Response({"message": "Welcome Teacher"})


class EducationDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsEducationOfficer]

    def get(self, request):
        return Response({"message": "Welcome Education Officer"})


class FinanceDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceOfficer]

    def get(self, request):
        return Response({"message": "Welcome Finance Officer"})
    
    

