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
        print("DEBUG : user =", request.user)
        print("DEBUG : obj.author =", obj.author)
        print("DEBUG : obj.issue.project.contributors =", list(obj.issue.project.contributors.all()))
        
        if request.method in permissions.SAFE_METHODS:
            return obj.issue.project.contributors.filter(user=request.user).exists()
        return obj.author == request.user


class IsProjectAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour les contributeurs
        if request.method in permissions.SAFE_METHODS:
            return obj.contributors.filter(user=request.user).exists()

        # Écriture autorisée uniquement pour l’auteur
        return obj.author == request.user
    
class IsIssueAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.project.contributors.filter(user=request.user).exists()
        return obj.author == request.user

class IsContributor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj peut être un Project, Issue ou Comment
        if isinstance(obj, Project):
            return obj.contributors.filter(user=request.user).exists()
        elif isinstance(obj, Issue):
            return obj.project.contributors.filter(user=request.user).exists()
        elif isinstance(obj, Comment):
            return obj.issue.project.contributors.filter(user=request.user).exists()
        return False
