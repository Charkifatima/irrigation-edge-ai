
# 02 – Target Definition

## 1. Objectif

Définir la variable cible du modèle de prévision des besoins en irrigation.

## 2. Variable cible proposée

Nom : net_irrigation_requirement

Description : quantité nette d'eau qu'il est nécessaire d'apporter par irrigation à une parcelle pour la période de prédiction.

Unité : mm.

Horizon proposé : prochaines 24 heures.

Type de problème : régression supervisée.

Statut : proposition à valider avec le Product Owner et le professeur.

## 3. Différence entre ET0, ETc et le besoin d'irrigation

### ET0 – Évapotranspiration de référence

ET0 représente la demande évaporative de l'atmosphère pour une surface de référence.

Elle est calculée à partir des données météorologiques avec la méthode FAO Penman-Monteith.

Unité : mm/jour.

### ETc – Évapotranspiration de la culture

ETc représente l'évapotranspiration estimée d'une culture dans des conditions standard.

Formule :

ETc = ET0 × Kc

Où :
- ET0 : évapotranspiration de référence.
- Kc : coefficient cultural selon la culture et le stade de croissance.

Unité : mm/jour.

### Besoin net d'irrigation

Il représente la quantité d'eau nette à apporter à la zone racinaire après prise en compte des réserves en eau du sol et des apports efficaces.

ETc et besoin net d'irrigation ne sont pas équivalents.

## 4. Méthode de construction du label

La méthode proposée est basée sur le bilan hydrique de la zone racinaire décrit dans FAO-56.

Équation du bilan hydrique :

Dr,i = Dr,i-1 - (P - RO) - I - CR + ETc + DP

Où :
- Dr : déficit hydrique de la zone racinaire (mm).
- P : précipitations (mm).
- RO : ruissellement (mm).
- I : irrigation nette infiltrée (mm).
- CR : remontée capillaire (mm).
- ETc : évapotranspiration de la culture (mm).
- DP : drainage profond (mm).

Pour construire une cible, le déficit hydrique est projeté sur les prochaines 24 heures sans irrigation.

Une règle agronomique doit ensuite définir le déficit cible à ne pas dépasser.

Formule conceptuelle :

I_net = max(0, Dr_projected - Dr_target)

Où :
- Dr_projected : déficit projeté sans irrigation.
- Dr_target : déficit hydrique souhaité après irrigation.

La valeur de Dr_target doit être définie et justifiée selon la stratégie d'irrigation retenue.

Attention : cette formule est une règle de construction simplifiée. Les termes du bilan hydrique, les pertes et les hypothèses doivent être correctement estimés avant son utilisation.

## 5. Besoin brut d'irrigation

Le besoin brut tient compte de l'efficacité du système d'irrigation.

I_brut = I_net / efficacité

L'efficacité doit être renseignée selon le système d'irrigation et les données disponibles.

Le besoin net reste la cible proposée pour le modèle.

## 6. Conversion en volume d'eau

1 mm d'eau sur 1 m² = 1 litre.

Volume net (L) = Besoin net (mm) × Surface (m²)

## 7. Variables nécessaires pour construire le label

- Date et coordonnées de la parcelle.
- Type de culture.
- Stade de croissance.
- ET0.
- Kc.
- ETc.
- Précipitations efficaces.
- Déficit hydrique initial.
- Caractéristiques de la zone racinaire.
- Propriétés hydriques du sol.
- Éventuels apports d'irrigation.

## 8. Validation nécessaire

Les éléments suivants doivent être validés :

- Variable cible : besoin net d'irrigation.
- Unité : mm.
- Horizon : 24 heures.
- Méthode : bilan hydrique FAO-56.
- Déficit cible après irrigation.
- Valeurs de Kc et profondeurs racinaires selon les cultures.
- Traitement de la pluie efficace et des pertes.

## 9. Statut

Version : V0.1

Statut : définition proposée, validation agronomique nécessaire.
