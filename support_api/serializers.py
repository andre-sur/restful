from rest_framework import serializers
from .models import CustomUser, Project, Contributor, Issue, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'age', 'can_be_contacted', 'can_data_be_shared']

    def validate_age(self, value):
            if value < 15:
                raise serializers.ValidationError("L'utilisateur doit avoir au moins 15 ans.")
            return value

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
    
    def validate_title(self, value):
        return value.capitalize()

    description = serializers.CharField(
    required=True,
    max_length=100,
    error_messages={
        'required': 'Merci de fournir une description.',
        'blank': 'La description ne peut pas être vide.',
        'max_length': 'La description ne peut pas dépasser 100 caractères.'
    }
)
    title = serializers.CharField(
    required=True,
    max_length=30,
    error_messages={
        'required': 'Merci de fournir un titre.',
        'blank': 'Le titre ne peut pas être vide.',
        'max_length': 'Le titre ne peut pas dépasser 30 caractères.'
    }
)

    def validate(self, data):
        if data.get('title') == data.get('description'):
            raise serializers.ValidationError("Le titre et la description doivent être différents.")
        return data


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = '__all__'

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
    
    def create(self, validated_data):
        author = validated_data.get('author')

        if not CustomUser.objects.filter(id=author.id).exists():
            raise serializers.ValidationError({'author': "L'auteur spécifié n'existe pas."})

        # Créer le commentaire si l'auteur est valide
        return Comment.objects.create(**validated_data)
