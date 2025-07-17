from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProjectViewSet, IssueViewSet, CommentViewSet, ContributorViewSet, UserViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')  
router.register(r'issues', IssueViewSet, basename='issue')  
router.register(r'comments', CommentViewSet, basename='comment')  
router.register(r'contributors', ContributorViewSet, basename='contributor') 
router.register(r'users', UserViewSet, basename='user')
urlpatterns = [
    path('', include(router.urls)),  # Inclut toutes les URL générées par le router
]
