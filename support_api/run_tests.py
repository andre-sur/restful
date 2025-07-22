import unittest
import sys

# Test suite à charger
loader = unittest.TestLoader()
suite = loader.discover('support_api', pattern='tests.py')

# Rediriger stdout dans un fichier
with open('resultats_tests.txt', 'w', encoding='utf-8') as f:
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    result = runner.run(suite)

# Facultatif : print résumé dans la console
print(f"Tests exécutés: {result.testsRun}, Erreurs: {len(result.errors)}, Echecs: {len(result.failures)}")
