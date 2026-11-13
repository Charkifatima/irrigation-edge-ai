# Irrigation Edge AI

Prévision des besoins en irrigation par IA à l’edge — projet Master IA et Systèmes Embarqués.

## État du projet

Le socle Python et les conventions Git ont été livrés avec [TMGROUP-9](https://dataopsfsa.atlassian.net/browse/TMGROUP-9).

[TMGROUP-10](https://dataopsfsa.atlassian.net/browse/TMGROUP-10) ajoute un environnement Docker de développement et un simulateur CPU de capteurs. La simulation produit des mesures synthétiques ; elle ne réalise ni prédiction IA ni commande d’irrigation. Kafka, PostgreSQL, Airflow, le Model Registry, l’API et le dashboard restent à intégrer.

## Démarrer avec Docker

Suivre [le guide Docker et simulation edge](docs/DOCKER.md) pour les prérequis, les tests et les preuves à fournir pour la revue.

```bash
docker compose config -q
docker compose build dev
docker compose run --rm dev python -m unittest discover -s tests -v
docker compose run --rm edge-sim
```

Le simulateur affiche 20 mesures JSON puis s’arrête. Chaque service est limité à 256 Mio et 1 CPU ; l’usage réel sur le PC cible reste à mesurer.

## Prérequis

- Git
- Python 3.11 ou supérieur, avec `pip` et `venv`
- Pour ce socle : aucun GPU, Docker ou service externe nécessaire

## Installation sous Ubuntu

```bash
git clone https://github.com/Charkifatima/irrigation-edge-ai.git
cd irrigation-edge-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Si la création du venv indique que `ensurepip` est absent, installer le paquet `python3-venv` correspondant à son Python avant de réessayer.

Pour essayer TMGROUP-10 avant sa fusion, sélectionner `feature/TMGROUP-10-docker-simulation-edge` après le clonage et avant l’installation.

## Vérification

```bash
python -m irrigation_edge_ai
python -m unittest discover -s tests -v
```

La première commande affiche `Irrigation Edge AI : environnement Python opérationnel.` ; la seconde doit terminer par `OK` avec six tests exécutés sur la branche TMGROUP-10. Ces tests valident le démarrage du package et le simulateur, pas une prévision d’irrigation.

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
