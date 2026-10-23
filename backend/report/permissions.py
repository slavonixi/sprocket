from rest_framework.permissions import BasePermission

class CanPlanOperation(BasePermission):
    """
    check if the user can plan an operation
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perm('report.can_plan_operation')

class CanStartOperation(BasePermission):
    """
    check if the user can start an operation
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perm('report.can_start_operation')

class CanPlanReport(BasePermission):
    """
    check if the user can start an operation
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perm('report.can_plan_report')

class CanStartReport(BasePermission):
    """
    check if the user can start an operation
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perm('report.can_start_report')
