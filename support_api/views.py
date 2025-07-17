from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Contributor, Issue, Comment, CustomUser
from .serializers import *
from .permissions import IsContributorOrAuthor, IsCommentAuthorOrReadOnly

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributorOrAuthor]  

    def get_queryset(self):
        return Project.objects.filter(contributors__user=self.request.user)

    def perform_create(self, serializer):
        # Lors de la création d'un projet, on assigne automatiquement l'utilisateur connecté comme auteur et contributeur
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributorOrAuthor]  # Utiliser IsContributorOrAuthor ici

    def get_queryset(self):
        # l'utilisateur doit être contributeur
        return Issue.objects.filter(project__contributors__user=self.request.user)

    def perform_create(self, serializer):
        # une issue créée est attribuée à l'auteur automatiquement
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]  # Permissions plus spécifiques pour les commentaires

    def get_queryset(self):
        # Seuls les commentaires des issues auxquelles l'utilisateur est contributeur sont retournés
        return Comment.objects.filter(issue__project__contributors__user=self.request.user)

    def perform_create(self, serializer):
        # Lors de la création d'un commentaire, on l'assigne automatiquement à l'utilisateur connecté comme auteur
        serializer.save(author=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # On ajoute un message dans la réponse
        response.data['note'] = "L'auteur a été automatiquement défini comme l'utilisateur connecté."
        return response

class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

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
