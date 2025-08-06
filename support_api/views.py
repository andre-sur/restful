from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Contributor, Issue, Comment, CustomUser
from .serializers import *
from .permissions import *
from django.db.models import Q
from django.db import models
from rest_framework.exceptions import ValidationError




class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.filter(
            Q(contributors__user=user) | Q(author=user)
        ).distinct().order_by('id')
        print(f"[VIEW DEBUG] get_queryset for user {self.request.user.id} (username: {self.request.user.username}) returns: {[p.id for p in qs]}")
        
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"[VIEW DEBUG] Retrieved project object ID: {instance.id}, author_id: {instance.author_id}")
        return super().retrieve(request, *args, **kwargs)


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
 
    #permission_classes = [permissions.IsAuthenticated, IsContributorOrAuthor]
    permission_classes = [permissions.IsAuthenticated, IsIssueAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Issue.objects.filter(
            Q(project__contributors__user=user) | Q(project__author=user)
        ).distinct().order_by('created_time')
    
    def get_object(self):
        try:
            # On récupère l'issue sans filtrer par user
            obj = Issue.objects.select_related('project', 'author', 'assignee').get(pk=self.kwargs["pk"])
        except Issue.DoesNotExist:
            raise NotFound("Issue non trouvée.")
        
        # Vérifie les permissions spécifiques à cet objet
        self.check_object_permissions(self.request, obj)
        return obj
    
    def get_serializer_class(self):
        if self.action == 'list':
            return IssueListSerializer
        return IssueSerializer

    def perform_create(self, serializer):
        user = self.request.user
        assignee = serializer.validated_data.get('assignee', None)
        if not assignee:
            serializer.save(author=user, assignee=user)
        else:
            serializer.save(author=user)

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsCommentAuthorOrReadOnly
from django.db.models import Q

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        comments = Comment.objects.filter(
            Q(issue__project__contributors__user=user) |
            Q(issue__project__author=user)
        ).distinct().order_by('id')
        return comments

    def perform_create(self, serializer):
        request_data = self.request.data

        # Vérification explicite : l'utilisateur ne doit pas envoyer le champ 'author'
        if 'author' in request_data:
            raise ValidationError({
                "author": "Ne spécifiez pas ce champ. L'auteur est automatiquement défini comme l'utilisateur connecté."
            })

        issue = serializer.validated_data['issue']
        project = issue.project
        user = self.request.user

        is_author = project.author == user
        is_contributor = project.contributors.filter(user=user).exists()

        if not (is_author or is_contributor):
            raise PermissionDenied("Vous devez être contributeur ou auteur du projet pour commenter cette issue.")

        serializer.save(author=user)

        def create(self, request, *args, **kwargs):
            response = super().create(request, *args, **kwargs)
            response.data['note'] = "L'auteur a été automatiquement défini comme l'utilisateur connecté."
            return response

class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsContributor,permissions.IsAuthenticated]

    def get_queryset(self):
        return Contributor.objects.filter(project__contributors__user=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsSelfOrSuperUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Ici on crée l'utilisateur avec create_user() pour le password hashé
        password = serializer.validated_data.pop('password', None)
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance and not request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Vous ne pouvez accéder qu'à votre propre profil.")
        return super().retrieve(request, *args, **kwargs)

class RegisterView(APIView):
    """
    View pour enregistrer un nouvel utilisateur.
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)