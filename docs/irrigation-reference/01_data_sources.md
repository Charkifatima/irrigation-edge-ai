
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

## 3. Tableau récapitulatif

| Source | Variables principales | Fréquence | Utilisation |
|---|---|---|---|
| Open-Meteo | Météo, ET0, humidité du sol estimée | Horaire/journalière | Variables climatiques |
| SoilGrids | Texture et propriétés du sol | Statique | Contexte du sol |
| Dataset marocain | Culture, parcelle, irrigation | Par observation/saison | Identification des parcelles |
| FAO-56 | Kc, ET0, ETc, bilan hydrique | Selon le calcul | Construction des références |

## 4. Points restant à vérifier

- Choisir la région pilote au Maroc.
- Sélectionner les cultures de la première version.
- Télécharger et inspecter les fichiers du dataset marocain.
- Vérifier les licences exactes des données utilisées.
- Identifier une source de prévisions météorologiques pour l'horizon futur de 24 heures.
- Identifier les données nécessaires pour estimer l'état hydrique initial du sol.

## 5. Statut

Version : V0.1

Statut : sources candidates identifiées, téléchargement et validation des données à effectuer.
