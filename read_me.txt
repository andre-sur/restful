Ce projet est une API RESTful construite avec Django
et Django REST Framework. 
Elle permet la gestion de projets collaboratifs via une base de données SQL comprenant les tables
utilisateurs (Users)
contributeurs (contributor)
problèmes (issues)
commentaires (comments) 

Un système de permissions permet d'organiser les autorisations d'accès.

Prérequis

Avant de commencer, assurez-vous d’avoir :

- Python 3.9+
- pip
- Git (facultatif, pour cloner le dépôt)
- Postman (pour tester les endpoints)

Créer et activer un environnement virtuel

python -m venv venv
source venv/bin/activate

Installer les dépendances

pip install -r requirements.txt

Appliquer les migrations
python manage.py migrate

Le superutilisateur est : 
nom : admin
mot de passe : admin

Pour lancer le serveur (nécessaire pour Postman et accès à la base de données via /admin)
python manage.py runserver

Puis, pour consulter et modifier la base de données (sur navigateur)
http://localhost:8000/admin


Pour les GET,POST, etc le projet est accessible via http://localhost:8000
Avec les terminaisons /api/...
projects
issues
users
comments

Exemple http://localhost:8000/api/issues/

On utilise ici Postman.

Pour obtenir un token, faire un POST vers http://localhost:8000/api/token/
Avec ceci (en raw) dans le body:
{
  "username": "elise_dev",
  "password": "difficile"
}

Puis récupérer le token access:
{
  "access": "votre_token_access",
  "refresh": "votre_token_refresh"
}


Lorsque vous faites une requête nécessitant un token (post, delete).

Option 1 : Copier/coller le token dans Authorization / Bearer Token

Option 2 : 
Copier le token dans le Header : 
a) sous forme de variable (si vous êtes dans un environnement avec des variables déclarées) - Bearer {{token}} 
b) ou bien tel quel 

Attention : expiration du token 90 mn (modifiable dans le setings.py)

Délai d'exporation modifiable dans RESTFUL/rest/settings.py

 'ACCESS_TOKEN_LIFETIME': timedelta(minutes=90),
 'REFRESH_TOKEN_LIFETIME': timedelta(days=7),