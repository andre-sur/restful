# permissions.py

from rest_framework import permissions

class IsContributorOrAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
       
        if obj.author == request.user:
            return True

        return obj.contributors.filter(user=request.user).exists()


class IsCommentAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return obj.author == request.user
