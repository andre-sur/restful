import os

import unittest
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))  # C:\Users\andre\Desktop\RESTFUL
sys.path.insert(0, PROJECT_DIR)
#sys.path.append(os.path.abspath(os.path.dirname(__file__)))
# 1. Définir la variable d'environnement pour les settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')

# 2. Initialiser Django
import django
django.setup()

# 3. Charger les tests
loader = unittest.TestLoader()
suite = loader.discover('support_api', pattern='tests.py')

# 4. Rediriger la sortie dans un fichier
with open('resultats_tests.txt', 'w', encoding='utf-8') as f:
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    result = runner.run(suite)

# 5. Afficher résumé dans la console
print(f"Tests exécutés: {result.testsRun}, Erreurs: {len(result.errors)}, Échecs: {len(result.failures)}")
