import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError 

# Définition du modèle CustomUser (utilisateur personnalisé)
class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)

    def is_rgpd_compliant(self):
        return self.age >= 15 and self.can_data_be_shared
    
    def clean(self):
        if self.username.strip().lower() == 'robert':
            raise ValidationError("Nom d'utilisateur 'robert' interdit.")

# Définition du modèle Project
class Project(models.Model):
    TYPE_CHOICES = [('BACK_END', 'Back-end'), ('FRONT_END', 'Front-end'), ('IOS', 'iOS'), ('ANDROID', 'Android')]
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects') 
    created_time = models.DateTimeField(auto_now_add=True)

# Définition du modèle Contributor
class Contributor(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributors')
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

# Définition du modèle Issue
class Issue(models.Model):
    PRIORITY_CHOICES = [('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')]
    TAG_CHOICES = [('BUG', 'Bug'), ('FEATURE', 'Feature'), ('TASK', 'Task')]
    STATUS_CHOICES = [('TO_DO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('FINISHED', 'Finished')]

    title = models.CharField(max_length=255)
    description = models.TextField()
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TO_DO')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_issues')  
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='assigned_issues')  
    created_time = models.DateTimeField(auto_now_add=True)

# Définition du modèle Comment
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Remplacé User par CustomUser
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    created_time = models.DateTimeField(auto_now_add=True)
