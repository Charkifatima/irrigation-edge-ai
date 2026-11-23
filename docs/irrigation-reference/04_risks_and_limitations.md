
# 04 – Risks and Limitations

## 1. Objectif

Ce document présente les risques, les incertitudes et les limites associés aux sources de données et à la construction des labels d'irrigation.

## 2. Risques liés aux données

### 2.1 Absence de mesures réelles d'irrigation

Problème :
Les datasets publics identifiés ne fournissent pas nécessairement les volumes d'eau réellement appliqués aux parcelles.

Conséquence :
Les labels pourraient être calculés à partir d'un modèle agronomique plutôt que mesurés sur le terrain.

Solution proposée :
Utiliser le bilan hydrique FAO-56 et identifier clairement les labels calculés. Ne pas les présenter comme des mesures réelles.

### 2.2 Données météorologiques estimées

Problème :
Les données historiques issues de réanalyses peuvent différer des mesures d'une station météorologique locale.

Conséquence :
Une différence entre les conditions météorologiques estimées et les conditions réelles de la parcelle peut affecter les calculs de ET0 et ETc.

Solution proposée :
Documenter la source, le modèle météorologique, les coordonnées et la période utilisée.

### 2.3 Humidité du sol

Problème :
L'humidité du sol issue d'un modèle ou d'une réanalyse ne correspond pas nécessairement à une mesure directe dans la zone racinaire.

Conséquence :
Le déficit hydrique calculé peut être incertain.

Solution proposée :
Privilégier les mesures de capteurs lorsque disponibles. Sinon, identifier clairement les estimations utilisées.

### 2.4 Caractéristiques du sol

Problème :
Les cartes pédologiques fournissent des estimations spatiales et ne décrivent pas nécessairement précisément chaque parcelle.

Conséquence :
La capacité au champ et le point de flétrissement peuvent être incertains.

Solution proposée :
Documenter les propriétés disponibles et rechercher des mesures locales si possible.

## 3. Risques agronomiques

### 3.1 Diversité des cultures

Problème :
Chaque culture possède ses propres coefficients Kc, profondeurs racinaires et calendriers de croissance.

Conséquence :
Une même valeur ET0 peut conduire à des valeurs ETc différentes.

Solution proposée :
Enregistrer le type de culture et le stade de croissance pour chaque observation.

### 3.2 Différences climatiques entre régions

Problème :
Les conditions météorologiques et les pratiques agricoles varient entre les régions marocaines.

Conséquence :
Un modèle entraîné sur une seule région peut ne pas bien généraliser à d'autres régions.

Solution proposée :
Conserver les coordonnées géographiques et la région de chaque parcelle. Évaluer les performances par région.

### 3.3 Construction du label

Problème :
Le besoin net d'irrigation dépend du déficit hydrique initial, de la pluie efficace, de ETc et de la stratégie d'irrigation.

Conséquence :
Un label calculé avec des hypothèses non validées peut être agronomiquement incorrect.

Solution proposée :
Documenter chaque hypothèse et faire valider la méthode par un spécialiste ou le professeur.

## 4. Risques techniques

### 4.1 Valeurs manquantes

Problème :
Certaines variables peuvent être absentes pour certaines dates ou parcelles.

Solution proposée :
Contrôler les valeurs manquantes avant la préparation du dataset et documenter les méthodes de traitement.

### 4.2 Différences de fréquence

Problème :
Les sources peuvent fournir des données horaires, journalières ou statiques.

Solution proposée :
Définir une période commune et documenter les règles d'agrégation et de synchronisation.

### 4.3 Fuite de données temporelle

Problème :
Des informations futures peuvent être accidentellement utilisées comme variables d'entrée pendant l'entraînement.

Solution proposée :
Séparer les données d'entraînement, de validation et de test selon le temps. Utiliser uniquement les informations disponibles au moment de la prédiction.

### 4.4 Généralisation du modèle

Problème :
Les cultures, sols et conditions climatiques peuvent varier entre les parcelles.

Solution proposée :
Évaluer le modèle sur des périodes et des parcelles qui n'ont pas servi à l'entraînement.

## 5. Limites actuelles du projet

- La région pilote n'est pas encore définitivement choisie.
- La liste des cultures reste à valider.
- Les mesures réelles d'irrigation restent à rechercher.
- Les propriétés hydriques du sol doivent être vérifiées.
- La méthode exacte de construction des labels doit être validée.
- Les sources de prévisions météorologiques à 24 heures doivent être confirmées.

## 6. Actions à réaliser

- Télécharger et examiner les datasets publics.
- Vérifier les licences et les conditions de réutilisation.
- Choisir la région pilote et les cultures.
- Identifier les variables réellement disponibles.
- Définir les hypothèses agronomiques.
- Construire un premier échantillon daté et traçable.
- Faire valider la définition du label.

## 7. Statut

Version : V0.1

Statut : risques identifiés, vérifications et validations en cours.
