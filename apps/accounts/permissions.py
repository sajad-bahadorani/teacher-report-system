from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"
    
    
class IsEducationOfficer(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "education"
    
    
class IsFinanceOfficer(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "finance"
