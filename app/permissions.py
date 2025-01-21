from rest_framework.permissions import BasePermission


class IsUserVerified(BasePermission):
    """
        Allow access only to users that are verified
    """
    def has_permission(self, request, view):
        return bool(request.user.is_verified)

class IsUserChef(BasePermission):
    """
    Allows access only to user who is a chef.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "chef")

class IsUserDriver(BasePermission):
    """
    Allows access only to user who is a driver.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "logistics")
    

class IsUserCustomer(BasePermission):
    """
    Allows access only to user who is a customer.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "customer")


class IsRestaurantUser(BasePermission):
    """
    Allows access only to user who is a restaurant or chef.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "chef")












