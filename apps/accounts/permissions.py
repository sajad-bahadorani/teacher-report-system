from rest_framework.permissions import BasePermission

from .models import User


class IsTeacher(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER
    
    
class IsEducationOfficer(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.EDUCATION_OFFICER
    
    
class IsFinanceOfficer(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.FINANCE_OFFICER
