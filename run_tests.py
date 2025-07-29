import os
import sys
import unittest
import coverage
from datetime import datetime

filename = f"resultats_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# 0. Configuration du chemin et variable d'env Django
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))  # C:\Users\andre\Desktop\RESTFUL
sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')

# 1. Initialiser Django
import django
django.setup()

# 2. Démarrer la couverture
cov = coverage.Coverage()
cov.start()

# 3. Charger la suite de tests
loader = unittest.TestLoader()
suite = loader.discover('support_api', pattern='tests.py')

# 4. Lancer les tests et rediriger la sortie vers fichier (ajout stamp filename)
with open(filename, 'w', encoding='utf-8') as f:
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    result = runner.run(suite)

    # 5. Arrêter et sauvegarder la couverture
    cov.stop()
    cov.save()

    # 6. Ajouter un résumé de la couverture dans le fichier
    f.write("\n\nRapport de couverture:\n")
    cov.report(file=f)

# 7. Afficher résumé des tests et couverture dans la console
print(f"Tests exécutés: {result.testsRun}, Erreurs: {len(result.errors)}, Échecs: {len(result.failures)}")
cov.report()
