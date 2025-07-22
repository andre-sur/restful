from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Project
from .serializers import ProjectSerializer

class ProjectAPIView(APIView):
    """
    APIView simple pour gérer les opérations CRUD sur Project.
    """

    def get(self, request, pk=None):
        """
        GET sans pk : liste tous les projets.
        GET avec pk : retourne un projet spécifique.
        """
        if pk:
            project = get_object_or_404(Project, pk=pk)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        else:
            projects = Project.objects.all()
            serializer = ProjectSerializer(projects, many=True)
            return Response(serializer.data)

    def post(self, request):
        """
        Crée un nouveau projet.
        """
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # exemple : on assigne l'auteur
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        """
        Met à jour entièrement un projet existant (remplacement complet).
        """
        if not pk:
            return Response({"detail": "Méthode PUT nécessite un 'pk'."}, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()  # sauvegarde les modifications
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        """
        Met à jour partiellement un projet (modification partielle).
        """
        if not pk:
            return Response({"detail": "Méthode PATCH nécessite un 'pk'."}, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Supprime un projet.
        """
        if not pk:
            return Response({"detail": "Méthode DELETE nécessite un 'pk'."}, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
