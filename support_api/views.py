from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Contributor, Issue, Comment, CustomUser
from .serializers import *
from .permissions import IsContributorOrAuthor, IsContributor,IsCommentAuthorOrReadOnly,IsIssueAuthorOrReadOnly,IsProjectAuthorOrReadOnly
from django.db.models import Q


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsContributor,permissions.IsAuthenticated, IsProjectAuthorOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(contributors__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
 # Utiliser IsContributorOrAuthor ici
    #permission_classes = [IsContributor,permissions.IsAuthenticated, IsIssueAuthorOrReadOnly]

    def get_queryset(self):
        # l'utilisateur doit être contributeur
        return Issue.objects.all()#temporaire
        #return Issue.objects.filter(project__contributors__user=self.request.user)

    def perform_create(self, serializer):
        # une issue créée est attribuée à l'auteur automatiquement
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsContributor,permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]  
  
    def get_queryset(self):
        return Comment.objects.all()#temporaire test
        #user = self.request.user
        #print("DEBUG: get_queryset for user =", user)

        #comments = Comment.objects.filter(
           # Q(issue__project__contributors__user=user) |
            #Q(issue__project__author=user)
        #).distinct()

#        print("DEBUG: Comments queryset IDs =", list(comments.values_list('id', flat=True)))
        return comments


    def perform_create(self, serializer):
        # l'auteur d'une commande qu'on créée est l'user connecté
        serializer.save(author=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # On ajoute un message dans la réponse
        response.data['note'] = "L'auteur a été automatiquement défini comme l'utilisateur connecté."
        return response

class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsContributor,permissions.IsAuthenticated]

    def get_queryset(self):
        # Retournons les contributeurs des projets auxquels l'utilisateur est contributeur
        return Contributor.objects.filter(project__contributors__user=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Assurez-vous que l'utilisateur soit authentifié

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
