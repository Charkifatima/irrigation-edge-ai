# Développement Docker et simulation edge — TMGROUP-10

## Objectif et limites

Exécuter le même socle Python sur les PC de l’équipe et simuler des mesures de capteurs sur CPU. Aucun ESP32 physique, GPU ou pilote spécifique n’est requis.

Cette simulation logicielle ne reproduit pas le matériel, les contraintes temps réel ou la précision d’un ESP32. Elle ne prédit pas encore l’irrigation et ne commande aucune pompe. Les mesures restent synthétiques, sans validité agronomique. Kafka et PostgreSQL seront intégrés dans les tâches suivantes : cette démo seule ne valide pas l’objectif complet du sprint.

## Prérequis

Sur Ubuntu, disposer de Docker Engine démarré et du plugin Docker Compose v2. Vérifier :

```bash
docker --version
docker compose version
docker info
```

Si `docker info` échoue, régler l’accès au moteur avant de continuer. En cas de message de permission sur le socket, utiliser temporairement `sudo docker ...` si le compte est autorisé, ou suivre la configuration officielle de l’équipe. Ne pas rendre le socket accessible à tous.

Installation officielle : https://docs.docker.com/engine/install/ubuntu/

## Récupérer la branche

Depuis le dépôt local, sans modifications non enregistrées :

```bash
git fetch origin
git switch feature/TMGROUP-10-docker-simulation-edge
```

Après fusion de la PR, travailler depuis `main` à jour.

## Compatibilité Docker Snap

Sur le PC cible, Python démarre avec `docker run --rm irrigation-edge-ai:dev python --version`, mais échoue avec `--security-opt no-new-privileges:true`. Le build a réussi ; l'exécution complète et les tests restent à valider après ce contournement.

Pour ce cas, utiliser le complément `compose.snap.yaml` : il retire uniquement l'option `no-new-privileges` des deux services. L'utilisateur non root, les capacités supprimées, le système de fichiers en lecture seule et les limites CPU/RAM restent appliqués. AppArmor n'est pas désactivé et aucun mode privilégié n'est ajouté. La configuration standard conserve `no-new-privileges` pour les autres machines.

Dans le terminal Ubuntu utilisé pour ce projet :

```bash
export COMPOSE_FILE=compose.yaml:compose.snap.yaml
docker compose config -q
docker compose run --rm dev
docker compose run --rm dev python -m unittest discover -s tests -v
docker compose run --rm edge-sim
```

Cette sélection s'applique au terminal courant : refaire l'export dans chaque nouveau terminal pour le projet. Pour revenir à la configuration standard : `unset COMPOSE_FILE`. Aucune reconstruction de l'image n'est nécessaire pour cette modification Compose.

Le tag `!reset []` retire la liste héritée au lieu de lui ajouter des valeurs : https://docs.docker.com/reference/compose-file/merge/#reset-value

## Construire et valider

À la racine du dépôt :

```bash
docker compose config -q
docker compose build dev
docker compose run --rm dev
# Résultat : Irrigation Edge AI : environnement Python opérationnel.
docker compose run --rm dev python -m unittest discover -s tests -v
# Résultat attendu : 6 tests, OK.
```

`Dockerfile` décrit l’image. `compose.yaml` décrit les deux services et leurs limites. `dev` monte `src` et `tests` en lecture seule : modifier les fichiers sur le PC puis relancer les tests suffit. Reconstruire l’image après changement des métadonnées du package ou du Dockerfile.

## Démonstration : 20 mesures

```bash
docker compose run --rm edge-sim
```

Le simulateur affiche une mesure JSON par ligne, environ chaque seconde, puis se termine normalement après 20 mesures. Il utilise le code embarqué dans l’image ; reconstruire avec `docker compose build dev` après une modification du simulateur.

Pour un test rapide et un fichier de preuve sur le PC :

```bash
mkdir -p data/raw
docker compose run --rm -T edge-sim python -m irrigation_edge_ai.simulator --count 20 --seed 42 --interval 0 > data/raw/edge-demo.jsonl
wc -l data/raw/edge-demo.jsonl
# Résultat attendu : 20 lignes.
head -n 1 data/raw/edge-demo.jsonl
```

Le fichier est ignoré par Git. La graine fixe les valeurs simulées ; les horodatages UTC reflètent l’heure réelle et changent à chaque exécution. Le schéma de démo est provisoire et devra être aligné avec le contrat de données du projet.

| Champ | Signification |
|---|---|
| `schema_version` | Version du format, actuellement 1 |
| `device_id` | Identifiant du capteur simulé |
| `simulated` | Toujours `true` pour ces données |
| `sequence` | Compteur de 1 à 20 par défaut |
| `timestamp_utc` | Horodatage UTC ISO 8601 |
| `soil_moisture_pct` | Humidité synthétique du sol en % |
| `air_temperature_c` | Température synthétique de l’air en °C |
| `relative_humidity_pct` | Humidité relative synthétique de l’air en % |

## Budget pour un PC de 8 Go

Chaque service est limité à 256 Mio de RAM et 1 CPU ; le démarrage n’exige aucun GPU. Lancer les commandes l’une après l’autre. La limite de mémoire est un plafond de configuration, pas une mesure de consommation. Le moteur Docker, la construction de l’image, Ubuntu et les autres logiciels consomment aussi des ressources. La construction n’est pas soumise à la limite mémoire du service.

Pour observer l’usage, lancer une simulation un peu plus longue :

```bash
docker compose run --rm edge-sim python -m irrigation_edge_ai.simulator --count 120 --interval 1
```

Pendant son exécution, dans un second terminal :

```bash
docker stats --no-stream
```

Conserver la sortie avec les résultats de tests pour la revue. Aucun port n’est publié ; les conteneurs s’exécutent avec un utilisateur non privilégié. Les données sont générées une à une pour éviter leur accumulation en mémoire.

## Reproductibilité et nettoyage

L’image Python est figée par digest et setuptools est fixé à `80.9.0`. La bibliothèque standard suffit à l’exécution. `dev` utilise le code de la branche locale ; `edge-sim` utilise celui de l’image construite. Le premier build nécessite Internet. Mettre à jour le digest explicitement lors d’une tâche de maintenance.

```bash
docker compose down
```

Les commandes `run --rm` suppriment déjà leurs conteneurs après l’exécution. Elles ne suppriment pas l’image ni le fichier de preuve local.

## Validation avant fusion

- Configuration Compose acceptée.
- Image construite et commande de démarrage réussie.
- Six tests réussis dans le conteneur.
- Vingt lignes JSON générées puis arrêt normal.
- Ressources observées sur le PC cible de 8 Go.
- PR liée à TMGROUP-10 relue par un équipier.

Références : https://docs.docker.com/reference/compose-file/services/ et https://hub.docker.com/_/python
