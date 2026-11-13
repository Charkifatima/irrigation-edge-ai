# Irrigation Edge AI

Prévision des besoins en irrigation par IA à l’edge — projet Master IA et Systèmes Embarqués.

## État du projet

Le socle Python et le simulateur CPU sont disponibles sur `main`. Le simulateur produit 20 mesures synthétiques JSONL. La V0.1 intégrée vise à publier ces 20 mesures dans Kafka, les lire avec le consumer ETL et les stocker dans PostgreSQL. Ces services restent à intégrer.

- [Diagrammes et contrat de données](docs/architecture.md)
- [Décisions d’architecture sur Confluence](https://dataopsfsa.atlassian.net/wiki/spaces/IRRIG/pages/5570561)

## Démo locale sur un PC de 8 Go

Prérequis Docker sous Ubuntu · Git, Docker Engine démarré et Docker Compose v2. Le premier build demande Internet. La démo utilise le CPU et des données synthétiques.

```bash
git clone https://github.com/Charkifatima/irrigation-edge-ai.git
cd irrigation-edge-ai
docker compose config -q
docker compose build dev
docker compose run --rm dev python -m unittest discover -s tests -v
docker compose run --rm edge-sim
```

Résultat attendu · six tests réussis, puis 20 lignes JSON et arrêt automatique. Chaque service est plafonné à 256 Mio et 1 CPU. Exécuter les commandes successivement pour limiter la charge. Les services centraux seront lancés selon l’étape de démonstration. Pour la future V0.1, seuls Kafka, PostgreSQL et le consumer seront nécessaires en plus du producteur. Le [guide Docker](docs/DOCKER.md) détaille la capture JSONL et la configuration pour Docker Snap.

### Exécution avec Python

Utiliser Python 3.11 ou supérieur avec `pip` et `venv`. Sous Ubuntu, installer le paquet `python3-venv` correspondant si `ensurepip` manque. Depuis la racine du dépôt cloné :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
python -m irrigation_edge_ai.simulator --count 20 --seed 42 --interval 0
```

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
