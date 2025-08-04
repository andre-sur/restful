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
 
    permission_classes = [permissions.IsAuthenticated, IsContributorOrAuthor]

    def get_queryset(self):
        return Issue.objects.select_related('project', 'author', 'assignee') \
        .filter(project__contributors__user=self.request.user) \
        .order_by('-created_time')
    
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
      
        serializer.save(author=self.request.user)
    
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
    permission_classes = [permissions.IsAuthenticated]  # Assurez-vous que l'utilisateur soit authentifié

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperUser()]  # seuls les superusers peuvent créer
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsSelfOrSuperUser()]
        return [permissions.IsAuthenticated()]
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsSelfOrSuperUser()]
        return [permissions.IsAuthenticated()]

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