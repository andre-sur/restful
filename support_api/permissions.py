# permissions.py
from support_api.models import Project, Issue, Comment

from rest_framework import permissions

class IsContributorOrAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Lecture : visible à tous les contributeurs
        if request.method in permissions.SAFE_METHODS:
            return obj.project.contributors.filter(user=request.user).exists()

        # Modification / suppression : seulement l'auteur
        return obj.author == request.user
    

class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return obj.issue.project.contributors.filter(user=request.user).exists()
        return obj.author == request.user

class IsProjectAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
       
        if request.method in permissions.SAFE_METHODS:
            return obj.contributors.filter(user=request.user).exists()

    
        return obj.author == request.user
    
class IsIssueAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.project.contributors.filter(user=request.user).exists()
        return obj.author == request.user

class IsContributor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if isinstance(obj, Project):
            return obj.contributors.filter(user=request.user).exists()
        elif isinstance(obj, Issue):
            return obj.project.contributors.filter(user=request.user).exists()
        elif isinstance(obj, Comment):
            return obj.issue.project.contributors.filter(user=request.user).exists()
        return False

class IsAgeCompliant(permissions.BasePermission):
    """
    Permet l'accès seulement si l'utilisateur a au moins 15 ans.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.age is not None and user.age >= 15


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsDataShareAllowed(permissions.BasePermission):
    """
    Permet l'accès seulement si l'utilisateur a donné son accord pour partager les données.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.can_data_be_shared
    
class IsSelfOrSuperUser(permissions.BasePermission):
    """
    Autorise les superusers à tout modifier.
    Sinon, un utilisateur ne peut modifier que son propre profil.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj == request.user