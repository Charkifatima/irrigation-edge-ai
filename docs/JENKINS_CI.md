# CI Jenkins — TMGROUP-27

## Objectif et état actuel

Cette pipeline Jenkins contrôle chaque branche et Pull Request avant revue : elle récupère le code, installe le package et les outils CI, exécute Ruff et Pytest, puis publie les résultats JUnit dans Jenkins. Elle n’utilise pas GitHub Actions et ne démarre aucun service Kafka, Airflow, PostgreSQL, MLflow ou Docker Compose.

Le dépôt est public. Lors de l’audit du 23 novembre 2026, aucun webhook GitHub n’était configuré. Un ruleset actif nommé « Limiter la fusion sur main » cible la branche par défaut, mais ses règles observées sont `deletion`, `non_fast_forward` et `update` : il ne requiert ni Pull Request ni statut de contrôle. L’API de protection classique indiquait également que `main` n’était pas protégée.

Une image Jenkins (`jenkins/jenkins:lts-jdk21`) et un conteneur `dataops-jenkins` arrêté existent déjà sur le PC. Le conteneur utilise le volume Docker `dataopstest_jenkins_data`, publie son port sur `127.0.0.1:8081` lorsqu’il fonctionne et n’a pas de limite mémoire/CPU configurée. Il n’a pas été démarré ni modifié. Réutiliser cette instance après vérification par son administrateur ; ne pas créer une deuxième instance ou toucher au volume existant sans autorisation.

## Fonctionnement du pipeline

Le [`Jenkinsfile`](../Jenkinsfile) est une Declarative Pipeline. Elle utilise `checkout scm` pour récupérer le commit sélectionné par Jenkins ; aucune branche n’est codée en dur, ce qui permet les builds de branches et de Pull Requests d’un job Multibranch.

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
  - **GitHub Branch Source** pour la découverte des branches et Pull Requests GitHub ;
  - **Git** et Git installé/configuré dans Jenkins pour le checkout.
- Une URL Jenkins stable, en HTTPS, joignable par GitHub pour les webhooks. Une adresse `localhost` ou un port privé du PC ne peut pas recevoir un webhook GitHub.

### Agent de build

Configurer un agent Linux qui exécute les étapes de shell et possède :

- Python 3.11 ou supérieur ;
- le module `venv` et `pip` associés à cet interpréteur (`python3-venv` sur Ubuntu si nécessaire) ;
- Git ;
- un accès réseau à PyPI pour installer les versions épinglées.

Le pipeline ne requiert ni GPU, ni Docker, ni Kafka, ni service de base de données. Utiliser de préférence un agent dédié plutôt que le nœud contrôleur Jenkins. Le code des Pull Requests est exécuté par l’agent : ne pas y exposer de secrets ni des identifiants privilégiés.

## Créer le job Jenkins

1. Réutiliser un Jenkins administré par l’équipe. Installer les plugins listés ci-dessus uniquement s’ils manquent.
2. Créer un job **Multibranch Pipeline**.
3. Ajouter une source **GitHub**, puis sélectionner `Charkifatima/irrigation-edge-ai`.
4. Définir les identifiants Jenkins nécessaires dans le magasin **Credentials** (jamais dans le dépôt). Le clonage d’un dépôt public peut être anonyme ; la publication de statuts et la création automatique des webhooks exigent des autorisations distinctes.
5. Activer la découverte des branches et des Pull Requests selon la stratégie de confiance de l’équipe, puis enregistrer et lancer un premier scan.
6. Jenkins découvre le `Jenkinsfile` sur chaque branche et utilise `checkout scm` pour construire le commit détecté. Vérifier qu’un agent portant les prérequis ci-dessus est disponible.

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

## PC avec 8 Go de RAM

La CI n’appelle que Python, Ruff et les tests unitaires : aucun service applicatif, conteneur de base de données ou calcul GPU n’est requis. Préférer un agent Linux à un exécuteur sur le contrôleur, limiter le nombre d’exécuteurs concurrents et éviter de lancer simultanément plusieurs builds lourds. Le conteneur Jenkins actuellement détecté n’a aucune limite mémoire/CPU ; vérifier et encadrer ses ressources avant toute remise en service.

Si aucune instance administrée ne peut être réutilisée, une instance Docker isolée peut être envisagée après autorisation : image Jenkins LTS officielle, volume nommé dédié, plafond d’environ 1 Gio et 1 CPU, et port HTTP publié uniquement sur `127.0.0.1`. Pour recevoir les webhooks, l’accès externe doit passer par un reverse proxy HTTPS contrôlé. Ne pas ajouter Jenkins à `compose.yaml` du projet et ne pas réutiliser ou supprimer le volume de l’instance existante.

## Validation de cette modification

L’état et les preuves réellement obtenues sont consignés dans la description de la Pull Request. Le Jenkinsfile n’est pas considéré comme exécuté tant qu’un build sur un Jenkins configuré n’a pas été observé. La revue par un autre membre de l’équipe, la configuration du webhook, la publication d’un statut GitHub et les règles de protection de `main` restent des actions de l’équipe.
