from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from support_api.models import Project, Contributor, Issue, Comment
from rest_framework.reverse import reverse

User = get_user_model()

class CommentPermissionsTest(TestCase):
    def setUp(self):
        # Création des utilisateurs
        self.author = User.objects.create_user(username='auteur', password='pass')
        self.contributor = User.objects.create_user(username='contrib', password='pass')
        self.stranger = User.objects.create_user(username='intrus', password='pass')

        # Création du projet et assignation des contributeurs
        self.project = Project.objects.create(title='Projet Test', description='desc', author=self.author)
        Contributor.objects.create(user=self.author, project=self.project)
        Contributor.objects.create(user=self.contributor, project=self.project)

        # Création d'une issue liée au projet
        self.issue = Issue.objects.create(title='Issue test', description='desc', project=self.project, author=self.author)

        # Création d'un commentaire sur l'issue
        self.comment = Comment.objects.create(description='Un commentaire', author=self.author, issue=self.issue)

        # Clients API pour chaque utilisateur
        self.client_author = APIClient()
        self.client_author.force_authenticate(user=self.author)

        self.client_contributor = APIClient()
        self.client_contributor.force_authenticate(user=self.contributor)

        self.client_stranger = APIClient()
        self.client_stranger.force_authenticate(user=self.stranger)

    def test_stranger_cannot_see_comment(self):
        # L'intrus tente d'accéder à la liste des commentaires
        response = self.client_stranger.get(f'/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, 404)  # Pas autorisé / introuvable

    def test_contributor_can_see_comment(self):
        response = self.client_contributor.get(f'/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, 200)

    def test_author_can_update_comment(self):
        data = {'description': 'Commentaire modifié'}
        response = self.client_author.patch(f'/comments/{self.comment.id}/', data, format='json')

       
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.description, 'Commentaire modifié')

    def test_contributor_cannot_update_comment(self):
        data = {'description': 'Modification non autorisée'}
        response = self.client_contributor.patch(f'/comments/{self.comment.id}/', data)
        self.assertEqual(response.status_code, 403)  # Forbidden
