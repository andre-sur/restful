import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')

import django
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from support_api.models import Project, Contributor, Issue, Comment

User = get_user_model()

class CommentPermissionsTest(TestCase):
    def setUp(self):
        # Création des utilisateurs
        self.author = User.objects.create_user(username='auteur', password='pass')
        self.contributor = User.objects.create_user(username='contrib', password='pass')
        self.stranger = User.objects.create_user(username='intrus', password='pass')

        # Création d'un projet avec contributeurs
        self.project = Project.objects.create(title='Projet Test', description='desc', type='BACK_END', author=self.author)
        Contributor.objects.create(user=self.author, project=self.project)
        Contributor.objects.create(user=self.contributor, project=self.project)

        # Création d'une issue liée au projet
        self.issue = Issue.objects.create(
            title='Issue test',
            description='desc',
            tag='BUG',
            priority='HIGH',
            project=self.project,
            author=self.author
        )

        # Création d'un commentaire lié à l'issue
        self.comment = Comment.objects.create(description='Un commentaire', author=self.author, issue=self.issue)

        # Clients authentifiés
        self.client_author = APIClient()
        self.client_author.force_authenticate(user=self.author)

        self.client_contributor = APIClient()
        self.client_contributor.force_authenticate(user=self.contributor)

        self.client_stranger = APIClient()
        self.client_stranger.force_authenticate(user=self.stranger)

    def test_stranger_cannot_see_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        response = self.client_stranger.get(url)
        print(f"RESPONSE API cannot see comment {response}")
        self.assertEqual(response.status_code, 403)  # Non-contributeur = pas d'accès

    def test_contributor_can_see_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        response = self.client_contributor.get(url)
        print(f"RESPONSE contributor can see {response}")
        self.assertEqual(response.status_code, 200)

    def test_author_can_update_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        data = {'description': 'Commentaire modifié'}
        response = self.client_author.patch(url, data, format='json')
        print(f"RESPONSE CORRECTED author can update {response}")
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.description, 'Commentaire modifié')

    def test_contributor_cannot_update_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        data = {'description': 'Modification non autorisée'}
        response = self.client_contributor.patch(url, data, format='json')
        print(f"RESPONSE 2 {response}")
        self.assertEqual(response.status_code, 403)
