# Irrigation Edge AI

Prévision des besoins en irrigation par IA à l’edge — projet Master IA et Systèmes Embarqués.

## État du projet

Ce socle correspond à [TMGROUP-9](https://dataopsfsa.atlassian.net/browse/TMGROUP-9) : structure Python, installation, test de démarrage et conventions Git.

La collecte des mesures, Kafka, PostgreSQL, Airflow, l’entraînement, le Model Registry, l’inférence edge, l’API et le dashboard seront développés dans les tâches suivantes. Aucun modèle de prévision ni service de données n’est encore implémenté.

## Prérequis

- Git
- Python 3.11 ou supérieur, avec `pip` et `venv`
- Pour ce socle : aucun GPU, Docker ou service externe nécessaire

## Installation sous Ubuntu

```bash
git clone https://github.com/Charkifatima/irrigation-edge-ai.git
cd irrigation-edge-ai
# Avant fusion de TMGROUP-9, sélectionner la branche de travail :
git switch feature/TMGROUP-9-initialisation-projet
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Si la création du venv indique que `ensurepip` est absent, installer le paquet `python3-venv` correspondant à son Python avant de réessayer.

Après fusion de la Pull Request, rester sur `main` et omettre la commande `git switch` de cette installation.

## Vérification

```bash
python -m irrigation_edge_ai
python -m unittest discover -s tests -v
```

La première commande affiche `Irrigation Edge AI : environnement Python opérationnel.` ; la seconde doit terminer par `OK` avec un test exécuté. Ce test valide le démarrage du package, pas une prévision d’irrigation.

## Organisation

| Chemin | Rôle |
|---|---|
| `src/irrigation_edge_ai/` | Package Python du projet |
| `tests/` | Tests automatisés |
| `data/` | Règles de gestion et dossiers de données locales |
| `docs/CONTRIBUTING.md` | Conventions de branches, commits et revues |
| `.github/pull_request_template.md` | Modèle commun de Pull Request |
| `pyproject.toml` | Métadonnées et installation du package |
| `.gitignore` | Exclusion des environnements, secrets et données générées |

## Contribution

Lire [les conventions de l’équipe](docs/CONTRIBUTING.md). Chaque changement passe par une branche liée à un ticket Jira puis une Pull Request vers `main`, relue par un autre équipier.

Ne jamais commiter les fichiers `.env`, mots de passe, clés privées ou données locales. Les dossiers `data/raw/` et `data/processed/` sont ignorés, sauf leurs fichiers `.gitkeep`.
