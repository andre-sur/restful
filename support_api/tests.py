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

     # Création du superuser 
        self.superuser = User.objects.create_superuser(username='superuser', password='pass', age=40)
        self.client_superuser = APIClient()
        self.client_superuser.force_authenticate(user=self.superuser)

# CATEGORIE - COMMENT ====================================================================

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

# CATEGORIE - USER ====================================================================

    def test_cannot_create_user_with_age_under_15(self):
        url = '/api/users/'
        data = {
            "username": "jeune",
            "password": "difficile",
            "email": "jeune@example.com",
            "age": 12,
            "can_be_contacted": False,
            "can_data_be_shared": False
        }
        response = self.client_superuser.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("age", response.data)

# CATEGORIE - ISSUES ====================================================================

    def test_author_can_update_issue(self):
        url = f'/api/issues/{self.issue.id}/'
        data = {'title': 'Titre modifié', 'priority': 'LOW'}
        response = self.client_author.patch(url, data, format='json')
        print(f"RESPONSE author update issue: {response}")
        self.assertEqual(response.status_code, 200)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.title, 'Titre modifié')
        self.assertEqual(self.issue.priority, 'LOW')

    
def test_contributor_can_list_issues(self):
    url = f'/api/issues/'
    response = self.client_contributor.get(url)
    print(f"RESPONSE contributor list issues: {response.data}")

    self.assertEqual(response.status_code, 200)

    results = response.data['results']

    self.assertIsInstance(results, list)
    self.assertTrue(any(issue['id'] == self.issue.id for issue in results))



    def test_contributor_can_view_specific_issue(self):
        url = f'/api/issues/{self.issue.id}/'
        response = self.client_contributor.get(url)
        print(f"RESPONSE contributor view issue detail: {response}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(self.issue.id))


# CATEGORIE - PROJECT ====================================================================

    def test_contributor_can_view_project(self):
        url = f'/api/projects/{self.project.id}/'
        response = self.client_contributor.get(url)
        print(f"RESPONSE contributor can view project: {response.status_code}")
        self.assertEqual(response.status_code, 200)

    def test_stranger_cannot_view_project(self):
        url = f'/api/projects/{self.project.id}/'
        response = self.client_stranger.get(url)
        print(f"RESPONSE stranger cannot view project: {response.status_code}")
        self.assertEqual(response.status_code, 404)


    def test_author_can_update_project(self):
        url = f'/api/projects/{self.project.id}/'
        data = {'title': 'Projet modifié'}
        response = self.client_author.patch(url, data, format='json')
        print(f"RESPONSE author update project: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Projet modifié')

    def test_contributor_cannot_update_project(self):
        url = f'/api/projects/{self.project.id}/'
        data = {'title': 'Modification non autorisée'}
        response = self.client_contributor.patch(url, data, format='json')
        print(f"RESPONSE contributor update project forbidden: {response.status_code}")
        self.assertEqual(response.status_code, 403)
