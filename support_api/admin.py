from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project, Contributor, Issue, Comment

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


