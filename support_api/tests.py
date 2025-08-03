import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')

import django
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from support_api.models import Project, Contributor, Issue, Comment

User = get_user_model()

# --- Classe commune pour setup partagé ---
class BaseTestCase(TestCase):
    def setUp(self):
        # Utilisateurs
        self.author = User.objects.create_user(username='auteur', password='pass')
        self.contributor = User.objects.create_user(username='contrib', password='pass')
        self.stranger = User.objects.create_user(username='intrus', password='pass')
        print(f"Setup Users: author={self.author.id}, contributor={self.contributor.id}, stranger={self.stranger.id}")

        # Projet
        self.project = Project.objects.create(title='Projet Test', description='desc', type='BACK_END', author=self.author)
        Contributor.objects.create(user=self.author, project=self.project)
        Contributor.objects.create(user=self.contributor, project=self.project)
        print(f"Setup Project: project_id={self.project.id}")

        # Issue
        self.issue = Issue.objects.create(
            title='Issue test',
            description='desc',
            tag='BUG',
            priority='HIGH',
            project=self.project,
            author=self.author
        )
        print(f"Setup Issue: issue_id={self.issue.id}")

        # Commentaire
        self.comment = Comment.objects.create(description='Un commentaire', author=self.author, issue=self.issue)
        print(f"Setup Comment: comment_id={self.comment.id}")

        # Clients authentifiés
        self.client_author = APIClient()
        self.client_author.force_authenticate(user=self.author)

        self.client_contributor = APIClient()
        self.client_contributor.force_authenticate(user=self.contributor)

        self.client_stranger = APIClient()
        self.client_stranger.force_authenticate(user=self.stranger)

        # Superuser
        self.superuser = User.objects.create_superuser(username='superuser', password='pass', age=40)
        self.client_superuser = APIClient()
        self.client_superuser.force_authenticate(user=self.superuser)
        print(f"Setup Superuser: superuser_id={self.superuser.id}")


# ===== Tests Commentaires =====
class CommentPermissionsTest(BaseTestCase):

    def test_stranger_cannot_see_comment(self):
        print(">> Running test_stranger_cannot_see_comment")
        url = f'/api/comments/{self.comment.id}/'
        print(f"URL: {url} -- Stranger user ID: {self.stranger.id}")
        response = self.client_stranger.get(url)
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 404)

    def test_contributor_can_see_comment(self):
        print(">> Running test_contributor_can_see_comment")
        url = f'/api/comments/{self.comment.id}/'
        print(f"URL: {url} -- Contributor user ID: {self.contributor.id}")
        response = self.client_contributor.get(url)
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 200)

    def test_author_can_update_comment(self):
        print(">> Running test_author_can_update_comment")
        url = f'/api/comments/{self.comment.id}/'
        data = {'description': 'Commentaire modifié'}
        print(f"URL: {url} -- Author user ID: {self.author.id}")
        response = self.client_author.patch(url, data, format='json')
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.description, 'Commentaire modifié')

    def test_contributor_cannot_update_comment(self):
        print(">> Running test_contributor_cannot_update_comment")
        url = f'/api/comments/{self.comment.id}/'
        data = {'description': 'Modification non autorisée'}
        print(f"URL: {url} -- Contributor user ID: {self.contributor.id}")
        response = self.client_contributor.patch(url, data, format='json')
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 403)


# ===== Tests Users =====
class UserCreationTest(BaseTestCase):

    def test_cannot_create_user_with_age_under_15(self):
        print(">> Running test_cannot_create_user_with_age_under_15")
        url = '/api/users/'
        data = {
            "username": "jeune",
            "password": "difficile",
            "email": "jeune@example.com",
            "age": 12,
            "can_be_contacted": False,
            "can_data_be_shared": False
        }
        print(f"URL: {url} -- Superuser ID: {self.superuser.id}")
        response = self.client_superuser.post(url, data, format='json')
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 400)
        self.assertIn("age", response.data)


# ===== Tests Issues =====
class IssuePermissionsTest(BaseTestCase):

    def test_author_can_update_issue(self):
        print(">> Running test_author_can_update_issue")
        url = f'/api/issues/{self.issue.id}/'
        data = {'title': 'Titre modifié', 'priority': 'LOW'}
        print(f"URL: {url} -- Author user ID: {self.author.id}")
        response = self.client_author.patch(url, data, format='json')
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.title, 'Titre modifié')
        self.assertEqual(self.issue.priority, 'LOW')

    def test_contributor_can_list_issues(self):
        print(">> Running test_contributor_can_list_issues")
        url = f'/api/issues/'
        print(f"URL: {url} -- Contributor user ID: {self.contributor.id}")
        response = self.client_contributor.get(url)
        print(f"RESPONSE: status_code={response.status_code}, data={response.data}")
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertIsInstance(results, list)
        self.assertTrue(any(issue['id'] == self.issue.id for issue in results))

    def test_contributor_can_view_specific_issue(self):
        print(">> Running test_contributor_can_view_specific_issue")
        url = f'/api/issues/{self.issue.id}/'
        print(f"URL: {url} -- Contributor user ID: {self.contributor.id}")
        response = self.client_contributor.get(url)
        print(f"RESPONSE: status_code={response.status_code}, data={response.data}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.issue.id)


# ===== Tests Projects =====
class ProjectPermissionsTest(BaseTestCase):

    def test_contributor_can_view_project(self):
        print(">> Running test_contributor_can_view_project")
        url = f'/api/projects/{self.project.id}/'
        print(f"URL: {url} -- Contributor user ID: {self.contributor.id}")
        response = self.client_contributor.get(url)
        print(f"RESPONSE: status_code={response.status_code}, data={response.data}")
        self.assertEqual(response.status_code, 200)

    def test_stranger_cannot_view_project(self):
        print(">> Running test_stranger_cannot_view_project")
        url = f'/api/projects/{self.project.id}/'
        print(f"URL: {url} -- Stranger user ID: {self.stranger.id}")
        response = self.client_stranger.get(url)
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 403)

    def test_author_can_update_project(self):
        print(">> Running test_author_can_update_project")
        url = f'/api/projects/{self.project.id}/'
        data = {'title': 'Projet modifié'}
        print(f"URL: {url} -- Author user ID: {self.author.id}")
        response = self.client_author.patch(url, data, format='json')
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Projet modifié')

    def test_contributor_cannot_update_project(self):
        print(">> Running test_contributor_cannot_update_project")
        url = f'/api/projects/{self.project.id}/'
        data = {'title': 'Modification non autorisée'}
        print(f"URL: {url} -- Contributor user ID: {self.contributor.id}")
        response = self.client_contributor.patch(url, data, format='json')
        print(f"RESPONSE: status_code={response.status_code}")
        self.assertEqual(response.status_code, 403)
