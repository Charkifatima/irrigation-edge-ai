
# 01 – Data Sources

## 1. Objectif

Ce document identifie les sources de données publiques nécessaires au projet de prévision des besoins en irrigation par IA à l'Edge.

Le périmètre géographique envisagé est le Maroc. La région pilote et la liste définitive des cultures restent à valider.

## 2. Sources de données identifiées

### 2.1 Open-Meteo – Données météorologiques

- Site : https://open-meteo.com/
- Documentation historique : https://open-meteo.com/en/docs/historical-weather-api
- Type : données météorologiques historiques issues de réanalyses.
- Variables recherchées :
  - Température moyenne, minimale et maximale (°C).
  - Humidité relative (%).
  - Vitesse du vent (m/s).
  - Rayonnement solaire (MJ/m²/jour).
  - Précipitations (mm/jour).
  - Évapotranspiration de référence ET0 (mm/jour).
  - Humidité du sol estimée (m³/m³), selon disponibilité.
- Fréquence : horaire ou journalière selon la variable.
- Utilisation : caractériser les conditions météorologiques et obtenir ET0.
- Licence et conditions : vérifier les conditions applicables à l'API et conserver l'attribution de la source.

Limite : les données historiques de réanalyse sont des estimations produites à partir d'observations et de modèles. Elles ne représentent pas nécessairement les mesures d'une station située dans la parcelle.

Pour une prédiction future à 24 heures, utiliser une source de prévisions météorologiques et non uniquement l'API historique.

### 2.2 SoilGrids – Caractéristiques des sols

- Site : https://soilgrids.org/
- Documentation : https://docs.isric.org/globaldata/soilgrids/
- Organisme : ISRIC – World Soil Information.
- Résolution spatiale : environ 250 mètres.
- Variables disponibles :
  - Pourcentage de sable.
  - Pourcentage de limon.
  - Pourcentage d'argile.
  - Densité apparente.
  - Carbone organique.
  - pH.
- Utilisation : caractériser le contexte pédologique des parcelles.
- Licence : CC BY 4.0.

Limites :
- Les propriétés sont des prédictions cartographiques, pas des analyses directes de chaque parcelle.
- La capacité au champ (FC) et le point de flétrissement permanent (PWP) ne sont pas fournis directement comme variables standard.
- L'API REST SoilGrids est actuellement signalée comme temporairement suspendue. Étudier les accès alternatifs WCS ou WebDAV.

### 2.3 Dataset marocain – Cultures et systèmes d'irrigation

- Article scientifique : https://www.nature.com/articles/s41597-026-06993-y
- Données : https://doi.org/10.6084/m9.figshare.28486022.v2
- Zone : cinq régions agricoles marocaines :
  Gharb, Tadla, Doukkala, Haouz et Souss.
- Couverture : environ 10 000 parcelles agricoles géolocalisées.
- Cultures : environ 45 types.
- Informations disponibles :
  - Type de culture.
  - Localisation des parcelles.
  - Type de système d'irrigation.
  - Données géographiques et informations Sentinel-2/NDVI.
- Utilisation : identifier les cultures et les parcelles candidates.

Limite : ce dataset ne fournit pas directement les besoins journaliers en eau ni les volumes d'irrigation réellement appliqués.

Licence : vérifier la licence exacte et les conditions de réutilisation sur la fiche du dépôt avant redistribution.

### 2.4 FAO-56 – Référence agronomique

- Document : FAO Irrigation and Drainage Paper No. 56.
- Titre : Crop Evapotranspiration.
- Lien : https://www.fao.org/4/X0490E/X0490E00.htm
- Utilisation :
  - Calcul de ET0 avec la méthode FAO Penman-Monteith.
  - Calcul de ETc à partir de ET0 et Kc.
  - Estimation des besoins en eau des cultures.
  - Suivi du bilan hydrique de la zone racinaire.
  - Estimation de la réserve en eau disponible.

FAO-56 est une référence méthodologique et non un dataset de mesures journalières pour les parcelles marocaines.

### 2.5 Dataset agro-météorologique – Région Oriental (Maroc)

- Source : [Mendeley Data – Quality-controlled and gap-filled daily agro-meteorological dataset](https://data.mendeley.com/datasets/fncyjvrdnp/1)
- DOI : https://doi.org/10.17632/fncyjvrdnp.1
- Auteurs : Mohammed Berrahal et Noureddine Boussala.
- Zone géographique : région Oriental, nord-est du Maroc.
- Stations : 10 stations météorologiques automatiques.
- Période : du 5 décembre 2018 au 3 mars 2026.
- Nombre d'enregistrements dans le dataset original : 15 924 station-jours.
- Licence : CC BY 4.0.

Variables disponibles :
- Température moyenne, maximale et minimale.
- Humidité relative moyenne, maximale et minimale.
- Rayonnement solaire.
- Vitesse moyenne et maximale du vent.
- Précipitations.
- Évapotranspiration de référence (ET0), calculée selon FAO-56 Penman-Monteith et Hargreaves-Samani.

Utilisation dans le projet :
- Disposer de données météorologiques provenant de stations situées dans des zones agricoles marocaines.
- Étudier les conditions climatiques de la région Oriental.
- Alimenter les calculs d'ET0 et l'estimation des besoins en eau des cultures.
- Comparer les données de stations avec les données de réanalyse d'Open-Meteo.

Préparation réalisée :
- Le fichier `observations_meteo_reelles_oriental.csv` a été intégré au dépôt GitHub.
- Un sous-ensemble a été préparé à partir du fichier original en conservant les indicateurs de qualité (`qc`), la provenance des valeurs (`src`) et les incertitudes (`unc`).

Limites :
- Les données concernent uniquement la région Oriental.
- Le dataset est contrôlé et complété : certaines valeurs sont reconstruites et ne sont donc pas des observations directes.
- Les indicateurs `qc` et `src` doivent être consultés avant toute utilisation.
- L'ET0 fournie est une valeur calculée et non une mesure directe.
- Le dataset ne contient pas les volumes d'irrigation réellement appliqués aux parcelles ni les labels réels des besoins en irrigation.

## 3. Tableau récapitulatif

| Source | Variables principales | Fréquence | Utilisation |
|---|---|---|---|
| Open-Meteo | Météo, ET0, humidité du sol estimée | Horaire/journalière | Variables climatiques |
| SoilGrids | Texture et propriétés du sol | Statique | Contexte du sol |
| Dataset marocain | Culture, parcelle, irrigation | Par observation/saison | Identification des parcelles |
| FAO-56 | Kc, ET0, ETc, bilan hydrique | Selon le calcul | Construction des références |
| Dataset agro-météorologique Oriental | Météo, précipitations, ET0 | Journalière | Données météorologiques de stations |

## 4. Points restant à vérifier

- Choisir la région pilote au Maroc.
- Sélectionner les cultures de la première version.
- Télécharger et inspecter les fichiers du dataset marocain.
- Vérifier les licences exactes des données utilisées.
- Identifier une source de prévisions météorologiques pour l'horizon futur de 24 heures.
- Identifier les données nécessaires pour estimer l'état hydrique initial du sol.

## 5. Statut

Version : V0.1

Statut : sources candidates identifiées. Un dataset agro-météorologique réel de la région Oriental a été téléchargé, préparé et intégré au dépôt GitHub. La validation des labels d'irrigation reste à réaliser.
