from rest_framework import serializers
from .models import CustomUser, Project, Contributor, Issue, Comment

# === User Serializer ===
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'age', 'can_be_contacted', 'can_data_be_shared']
        extra_kwargs = {
            'password': {'write_only': True},
            'age': {'required': True}
        }

    def validate_age(self, value):
        if value < 15:
            raise serializers.ValidationError("L'utilisateur doit avoir au moins 15 ans.")
        return value


# === Project Serializer ===
class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    title = serializers.CharField(
        required=True,
        max_length=30,
        error_messages={
            'required': 'Merci de fournir un titre.',
            'blank': 'Le titre ne peut pas être vide.',
            'max_length': 'Le titre ne peut pas dépasser 30 caractères.'
        }
    )
    description = serializers.CharField(
        required=True,
        max_length=100,
        error_messages={
            'required': 'Merci de fournir une description.',
            'blank': 'La description ne peut pas être vide.',
            'max_length': 'La description ne peut pas dépasser 100 caractères.'
        }
    )

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_time']

    def validate_title(self, value):
        return value.capitalize()

    def validate(self, data):
        if data.get('title') == data.get('description'):
            raise serializers.ValidationError("Le titre et la description doivent être différents.")
        return data


# === Contributor Serializer ===
class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = '__all__'
        read_only_fields = ['created_time']


# === Issue Serializer ===
class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
        read_only_fields = ['created_time']

    
    def validate(self, data):
        project = data.get('project')
        assignee = data.get('assignee')
        if assignee and not Contributor.objects.filter(project=project, user=assignee).exists():
            raise serializers.ValidationError({
    'assignee': "L'utilisateur assigné doit être un contributeur du projet."
})
        return data


# === Comment Serializer ===
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['id', 'created_time']

    def create(self, validated_data):
        author = validated_data.get('author')
        if not CustomUser.objects.filter(id=author.id).exists():
            raise serializers.ValidationError({'author': "L'auteur spécifié n'existe pas."})
        return Comment.objects.create(**validated_data)
