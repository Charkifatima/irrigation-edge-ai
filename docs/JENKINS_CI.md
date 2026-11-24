# CI Jenkins — TMGROUP-27

## Objectif et état actuel

Cette pipeline Jenkins contrôle chaque branche et Pull Request avant revue : elle récupère le code, installe le package et les outils CI, exécute Ruff et Pytest, puis publie les résultats JUnit dans Jenkins. Elle n’utilise pas GitHub Actions et ne démarre aucun service Kafka, Airflow, PostgreSQL, MLflow ou Docker Compose.

Le dépôt est public. L’audit local du 23 novembre 2026 confirme que `Jenkinsfile` est présent sur `main` (`e83617817eb9227ff3ec6b1bf0e8f9f451505b73`). Le conteneur `dataops-jenkins` fonctionne déjà depuis l’image `jenkins/jenkins:lts-jdk21` (Jenkins 2.580.2, Debian 13/Trixie, Java 21 et Git 2.47.3), mais aucun interpréteur Python n’y est installé. Son API refuse la lecture anonyme (HTTP 403, permission `Hudson.Read` manquante) : la configuration du job, ses nœuds et son dernier build n’ont donc pas pu être vérifiés ni déclenchés.

Le contrôleur utilise une limite de 1 Gio et 1 CPU, publie `127.0.0.1:8081` et monte uniquement le volume Jenkins `dataopstest_jenkins_data` sur `/var/jenkins_home`. Il n’est pas privilégié et aucun socket Docker n’y est monté. Les plugins Pipeline, Git, JUnit et **SSH Build Agents** sont présents ; aucun conteneur agent distinct n’a été trouvé. L’image locale `jenkins-python:local` est une image applicative Python 3.11.18, mais elle ne contient ni Git, ni Java, ni les outils Ruff/Pytest ; elle n’est pas utilisable telle quelle comme agent Jenkins.

L’architecture retenue ajoute un agent SSH Python isolé, sans remplacer, arrêter ou reconfigurer le contrôleur. Aucun volume, identifiant, paramètre ni job Jenkins existant n’a été modifié. L’agent est limité à 512 Mio et 1 CPU, sans port publié sur l’hôte et sans accès au socket Docker.

### Choix d’architecture

- **A — agent Python séparé (retenu)** : le plugin SSH Build Agents est déjà installé ; un agent dédié isole l’exécution des builds et n’a besoin d’aucun accès au socket Docker.
- **B — image Jenkins personnalisée** : elle ferait exécuter le code de build sur le contrôleur et nécessiterait de remplacer/recréer le conteneur actuel. Cette opération requiert une autorisation explicite et n’est pas nécessaire avec l’agent séparé.
- **C — réutiliser directement l’image applicative** : elle ne contient ni Git, Java, Ruff ou Pytest, et le conteneur Jenkins n’a pas d’accès Docker. Ajouter le socket Docker pour lancer l’image exposerait l’hôte sans nécessité.

## Fonctionnement du pipeline

Le [`Jenkinsfile`](../Jenkinsfile) est une Declarative Pipeline. Elle cible le label `irrigation-python` pour exécuter les builds hors du contrôleur et utilise `checkout scm` pour récupérer le commit sélectionné par Jenkins ; aucune branche n’est codée en dur.

1. **Checkout** — récupère le commit fourni par la configuration SCM du job.
2. **Setup Python** — sélectionne Python 3.11 ou `python3` (qui doit être 3.11+), crée `.venv`, installe les versions CI figées (`pip` 25.3, `setuptools` 80.9.0, Ruff 0.14.4 et Pytest 8.4.2), puis installe le projet sans dépendances runtime supplémentaires.
3. **Lint** — exécute `ruff check src tests`. Toute erreur Ruff fait échouer le build.
4. **Tests** — `python -m pytest` collecte également les tests `unittest` et écrit `reports/pytest.xml` au format JUnit.
5. **Publication** — le plugin JUnit affiche les résultats dans Jenkins. Si les tests échouent, le bloc `post` publie tout de même le XML généré. L’absence de rapport après des tests réussis est une erreur.
6. **Nettoyage** — le bloc `post { always { ... } }` publie d’abord le rapport, puis supprime l’espace de travail éphémère de ce build. Cela ne supprime ni le dépôt Git distant, ni un volume, ni les données d’un autre service.

Le pipeline utilise un délai maximal de 15 minutes. Un échec de checkout, d’environnement, de Ruff, de tests ou de publication entraîne un build `FAILURE`; les builds terminés correctement affichent `SUCCESS`.

## Prérequis

### Contrôleur Jenkins et plugins

- Jenkins LTS avec Java 21 (l’image déjà présente est basée sur `lts-jdk21`).
- Plugins Jenkins :
  - **Pipeline** (`workflow-aggregator`) pour la Declarative Pipeline et ses étapes ;
  - **JUnit** pour l’étape `junit` et les rapports de tests ;
  - **SSH Build Agents** pour lancer le nœud sur l’agent dédié ;
  - **GitHub Branch Source** pour la découverte des branches et Pull Requests GitHub ;
  - **Git** sur le contrôleur et l’exécutable Git sur l’agent pour le checkout.
- Une URL Jenkins stable, en HTTPS, joignable par GitHub pour les webhooks. Une adresse `localhost` ou un port privé du PC ne peut pas recevoir un webhook GitHub.

### Agent de build

L’agent reproductible est défini dans [`ci/jenkins-agent/`](../ci/jenkins-agent/) :

- image Python `3.11.18` basée sur le digest du `Dockerfile` applicatif ;
- Git `2.39.5`, OpenSSH server `9.2p1` et Java 17 installés depuis les versions Debian Bookworm épinglées dans le Dockerfile ;
- `pip` et `venv` de l’image Python, sans cache pip dans le système de fichiers en lecture seule ;
- ressources limitées à 512 Mio, 1 CPU et 128 processus ;
- système de fichiers en lecture seule, répertoire de travail temporaire, accès SSH par clé uniquement ;
- réseau Docker existant du contrôleur, sans publication de port ni montage du socket Docker.

L’image fournit Python, Git et Java ; Ruff, Pytest et les dépendances CI sont installés dans le virtualenv éphémère par le pipeline. Les builds de Pull Requests exécutent du code sur cet agent : ne lui fournir aucun secret de déploiement ou identifiant privilégié.

Le contrôleur courant appartient au réseau Docker `dataopstest_default`. Si le nom diffère après restauration, définir `JENKINS_DOCKER_NETWORK` avec le nom exact du réseau externe avant de lancer Compose. Le service échoue explicitement si ce réseau n’existe pas.

## Configurer le job Jenkins

1. Réutiliser l’instance Jenkins et le job existants `Irrigation-Edge-AI-CI`. Ne pas remplacer le conteneur ni son volume persistant pour cette correction.
2. Créer une clé SSH dédiée à l’agent, sous `ci/jenkins-agent/.secrets/` (ce répertoire est ignoré par Git), puis ajouter sa clé privée dans Jenkins **Credentials** comme identifiant SSH, utilisateur `ci`. Jenkins prend en charge les clés avec passphrase. Ne jamais copier la clé privée dans le dépôt, l’image ou un journal.

   ```bash
   install -d -m 700 ci/jenkins-agent/.secrets
   ssh-keygen -t ed25519 -C irrigation-jenkins-agent \
     -f ci/jenkins-agent/.secrets/agent
   cp ci/jenkins-agent/.secrets/agent.pub \
     ci/jenkins-agent/.secrets/authorized_keys
   chmod 600 ci/jenkins-agent/.secrets/agent
   ```

3. Vérifier que le fichier `ci/jenkins-agent/.secrets/authorized_keys` contient uniquement la clé publique correspondante.
4. Dans **Manage Jenkins → Nodes**, créer le nœud `irrigation-python-agent`, avec le label exact `irrigation-python`, un exécuteur, le répertoire distant `/home/ci/agent`, puis **Launch agents via SSH** vers `irrigation-ci-agent:2222` avec l’identifiant SSH dédié. Choisir une vérification d’empreinte d’hôte (ne pas désactiver la vérification) et confirmer l’empreinte ED25519 de l’agent.
5. Démarrer l’agent depuis la racine du dépôt :

   ```bash
   docker compose -f ci/jenkins-agent/compose.yaml up --build -d
   ```

   La commande construit uniquement l’image et le service de cet agent. Elle ne redémarre ni ne recrée `dataops-jenkins`. Le fichier Compose refuse de créer un réseau implicite et utilise le réseau Jenkins déjà existant.
6. Vérifier que le nœud est en ligne dans Jenkins, puis lancer un scan/build de la branche `main` dans le job `Irrigation-Edge-AI-CI`. Le nœud ne peut pas être configuré ni le job lancé depuis cette session : l’API Jenkins exige une authentification disposant de `Hudson.Read`.

L’empreinte publique de l’hôte SSH peut être lue avec `docker compose -f ci/jenkins-agent/compose.yaml exec python-agent ssh-keygen -lf /var/lib/jenkins-agent/hostkeys/ssh_host_ed25519_key.pub` et doit être vérifiée lors de l’approbation du nœud.

Pour arrêter uniquement ce nouvel agent, utiliser `docker compose -f ci/jenkins-agent/compose.yaml stop python-agent`. Ne pas supprimer le volume `irrigation-jenkins-agent-hostkeys` : il conserve la clé d’hôte utilisée pour vérifier l’identité SSH du nœud.

Un job Pipeline non-Multibranch est possible, mais doit avoir une configuration SCM compatible et sélectionner explicitement le dépôt et la branche à construire. Le job Multibranch est recommandé pour les PR.

## Webhook et statuts GitHub

Dans **Settings → Webhooks** du dépôt, configurer un webhook vers l’endpoint du plugin GitHub Branch Source, typiquement :

```text
https://jenkins.example.org/github-webhook/
```

Choisir `application/json`, protéger le webhook avec un secret stocké dans Jenkins/GitHub, et sélectionner les événements **Pushes** et **Pull requests**. Remplacer l’exemple par l’URL HTTPS réelle du Jenkins de l’équipe. Ne pas publier Jenkins directement sur Internet sans reverse proxy TLS et contrôles d’accès.

GitHub Branch Source peut intégrer les événements GitHub à l’indexation Multibranch. La création automatique du webhook dépend de la configuration du plugin et des droits de ses identifiants ; sinon, un administrateur du dépôt doit le créer manuellement. Aucun webhook n’était présent lors de l’audit.

La publication d’un résultat dans une PR dépend aussi du plugin, du type d’identifiant GitHub et de ses droits d’écriture de statuts/checks. Préférer une GitHub App dédiée, enregistrée dans le magasin d’identifiants Jenkins, avec les droits minimaux requis par le plugin (lecture du dépôt et des PR, écriture des statuts/checks ; gestion des webhooks seulement si Jenkins les crée). Un token personnel ne doit être ni inventé, ni placé dans Git. Après configuration, vérifier sur une PR que le check/status Jenkins apparaît réellement et que ses succès et échecs sont transmis.

Références : [Jenkins Multibranch Pipeline](https://www.jenkins.io/doc/book/pipeline/multibranch/) et [plugin GitHub Branch Source](https://plugins.jenkins.io/github-branch-source/).

## Exiger le contrôle avant fusion dans `main`

Une pipeline réussie et un webhook ne rendent pas un statut obligatoire. L’administrateur du dépôt doit :

1. Ouvrir **Settings → Rules → Rulesets** et modifier le ruleset « Limiter la fusion sur main » (ou créer une règle ciblant la branche par défaut).
2. Activer **Require a pull request before merging** et les approbations requises par la politique de l’équipe.
3. Après un premier build PR avec publication effective du résultat, ajouter le nom exact du statut/check Jenkins observé dans l’interface GitHub à **Require status checks to pass**. Le nom dépend du job, du plugin et de son contexte ; ne pas le deviner.
4. Enregistrer, puis vérifier par un test contrôlé qu’un check échoué bloque la fusion et qu’un check réussi permet la suite du processus.
5. Examiner les règles de contournement (bypass) afin qu’elles ne neutralisent pas ces exigences pour les acteurs concernés.

Les options disponibles peuvent dépendre du rôle de l’administrateur, des règles de l’organisation et du plan GitHub. Au moment de l’audit, le ruleset actif n’imposait ni revue de PR ni statut CI. Aucune permission ni règle GitHub n’a été modifiée dans cette tâche.

## Exécuter localement

Depuis la racine du dépôt, avec Python 3.11+ :

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install "pip==25.3" "setuptools==80.9.0" "ruff==0.14.4" "pytest==8.4.2"
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/ruff check src tests
mkdir -p reports
.venv/bin/python -m pytest -q tests --junitxml=reports/pytest.xml
```

Le fichier `reports/pytest.xml` est un artefact local de validation. Jenkins collecte son équivalent via le plugin JUnit avant le nettoyage du workspace.

## Lire les résultats

- **Console Output** indique l’étape qui a échoué et les diagnostics Ruff/Pytest.
- La vue **Test Result** de Jenkins présente le nombre de tests réussis, échoués ou ignorés et le détail des erreurs, grâce au XML JUnit.
- Le résultat du build est `SUCCESS` si toutes les étapes réussissent et `FAILURE` si l’une échoue. La pipeline affiche aussi ce résultat dans la sortie de fin.
- Dans GitHub, le check/status sur la PR n’est visible qu’après configuration et validation de l’intégration de statuts.

## Dépannage

| Symptôme | Vérification |
|---|---|
| `python3.11` ou Python 3.11+ introuvable | Vérifier le `PATH` de l’agent et la version de `python3` dans son environnement Jenkins. |
| `No module named venv` / erreur `ensurepip` | Installer le paquet `python3-venv` correspondant à l’interpréteur de l’agent. |
| Installation pip en échec | Vérifier l’accès réseau PyPI et la compatibilité des versions épinglées avec l’interpréteur de l’agent. |
| Ruff échoue | Lire les fichiers et lignes indiqués ; corriger le code plutôt que désactiver les règles. |
| Pytest échoue | Consulter `Console Output` et la vue **Test Result**. Les tests existants sont écrits avec `unittest` et sont collectés par Pytest. |
| Rapport JUnit absent ou invalide | Vérifier que la commande Pytest a été exécutée et que le plugin Jenkins **JUnit** est installé/à jour. |
| Aucun build après une PR | Vérifier le webhook, son URL HTTPS publique, les événements choisis, le scan Multibranch et les journaux Jenkins. |
| Aucun statut dans GitHub | Vérifier les identifiants Jenkins, leurs permissions d’écriture de statuts/checks, puis construire une PR et relever le nom exact du check. |

## Vérifier l’agent et les ressources

Après démarrage et connexion du nœud Jenkins, les vérifications suivantes doivent s’exécuter dans le conteneur agent :

```bash
docker compose -f ci/jenkins-agent/compose.yaml exec python-agent python3.11 --version
docker compose -f ci/jenkins-agent/compose.yaml exec python-agent python3.11 -m pip --version
docker compose -f ci/jenkins-agent/compose.yaml exec python-agent git --version
```

Le build Jenkins valide Ruff et Pytest sur le checkout réel et publie `reports/pytest.xml`. L’exécution locale de ces étapes dans l’image n’est qu’une validation de l’environnement agent ; elle ne remplace pas un build observé dans Jenkins.

## PC avec 8 Go de RAM

La CI n’appelle que Python, Ruff et les tests unitaires : aucun service applicatif, conteneur de base de données ou calcul GPU n’est requis. Le contrôleur existant est déjà limité à 1 Gio et 1 CPU ; l’agent ajoute au maximum 512 Mio et 1 CPU, avec un seul exécuteur. Éviter les builds simultanés non nécessaires sur cette machine.

### Retour arrière et limitations

Cette correction ne modifie pas l’instance Jenkins actuelle. Pour revenir en arrière, arrêter uniquement `python-agent` avec la commande ci-dessus et retirer/revertir le changement de label du `Jenkinsfile` via la revue Git habituelle. Conserver le volume dédié `irrigation-jenkins-agent-hostkeys` tant que le nœud est configuré. Le volume Jenkins `dataopstest_jenkins_data` n’est ni sauvegardé, ni remplacé, ni supprimé par cette procédure.

La connexion de l’agent exige une configuration manuelle du nœud et de son identifiant SSH dans Jenkins. Le build Jenkins n’est pas considéré comme validé avant qu’un administrateur ait connecté l’agent puis exécuté `Irrigation-Edge-AI-CI` sur `main`. Les versions du socle et des paquets sont figées ; leur mise à jour de sécurité doit être faite explicitement dans une modification ultérieure.

## Validation de cette modification

Dans l’image finale `irrigation-jenkins-python-agent:3.11.18`, exécutée avec l’utilisateur `ci`, le système de fichiers racine en lecture seule et les limites de l’agent :

- `docker build --pull=false -t irrigation-jenkins-python-agent:3.11.18 ci/jenkins-agent` — réussi.
- `docker compose -f ci/jenkins-agent/compose.yaml config --quiet` — réussi.
- `python --version` — `Python 3.11.18`.
- `python -m pip --version` — pip `24.0` dans l’image ; `pip 25.3` dans le virtualenv du pipeline.
- `git --version` — `git version 2.39.5`.
- `ruff check src tests` — réussi, `All checks passed!`.
- `python -m pytest -q tests --junitxml=reports/pytest.xml` — `6 passed`.
- Rapport JUnit généré et lu — 6 tests, 0 échec, 0 erreur.
- Commande distante SSH et transfert SFTP testés dans un conteneur éphémère — acceptés pour l’utilisateur UID 10001.
- `git diff --check` — réussi.

Le build Jenkins n’a pas été lancé : l’API de l’instance répond HTTP 403 sans authentification `Hudson.Read`, et la clé/nœud SSH doivent être configurés manuellement. La revue par un autre membre de l’équipe, la configuration du webhook, la publication d’un statut GitHub et les règles de protection de `main` restent des actions de l’équipe.
