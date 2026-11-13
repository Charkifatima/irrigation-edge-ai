"""Vérifie que le package installé est exécutable par un équipier."""
import subprocess
import sys
import unittest


class PackageSmokeTest(unittest.TestCase):
    def test_module_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "irrigation_edge_ai"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("environnement Python opérationnel", result.stdout)


if __name__ == "__main__":
    unittest.main()
