from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project, Contributor, Issue, Comment

# Enregistrer ton modèle CustomUser avec les paramètres d'admin par défaut


# Enregistrer les autres modèles
admin.site.register(Project)
admin.site.register(Contributor)
admin.site.register(Issue)
admin.site.register(Comment)

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Données RGPD", {
            "fields": ("age", "can_be_contacted", "can_data_be_shared"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


