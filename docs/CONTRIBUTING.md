# Travail en équipe

## Branches

`main` contient les changements relus et validés. Chaque tâche part d’une branche courte créée depuis `main` à jour. Aucun `develop` n’est nécessaire.

| Usage | Convention | Exemple |
|---|---|---|
| Fonctionnalité ou socle | `feature/TMGROUP-<id>-description` | `feature/TMGROUP-9-initialisation-projet` |
| Correction | `fix/TMGROUP-<id>-description` | `fix/TMGROUP-9-correction-installation` |
| Documentation | `docs/TMGROUP-<id>-description` | `docs/TMGROUP-9-guide-equipe` |

## Cycle d’une tâche

1. Passer la tâche Jira en cours lorsque le travail commence.
2. Mettre à jour `main`, puis créer la branche de la tâche.
3. Réaliser le changement et les tests applicables ; actualiser la documentation.
4. Commiter avec la clé Jira : `chore: TMGROUP-9 initialiser le socle Python`.
5. Pousser la branche et ouvrir une Pull Request vers `main`.
6. Mettre la clé Jira dans le titre et le lien du ticket dans la description.
7. Faire relire la PR par un autre membre de l’équipe, corriger les remarques, puis fusionner après validation.
8. Passer le ticket à Done seulement quand ses critères d’acceptation sont satisfaits.

Pour un changement de code : `feat`, `fix`, `test` ; pour la documentation : `docs` ; pour le socle : `chore`.

## Vérifications avant revue

```bash
python -m unittest discover -s tests -v
```

Vérifier aussi l’installation selon le README et l’absence de secrets ou données générées dans `git diff --cached`.

## Réglages GitHub à effectuer par le propriétaire

Inviter les équipiers avec leurs propres comptes GitHub. Configurer, selon les options disponibles pour le dépôt, la protection de `main` avec passage par PR et une approbation d’un autre membre. Ces réglages ne sont pas activés par les fichiers du dépôt.

La présence de la clé Jira facilite la traçabilité ; l’affichage automatique des branches et PR dans Jira dépend de la connexion GitHub–Jira configurée pour le projet.
