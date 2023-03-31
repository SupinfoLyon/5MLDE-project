# 5MLDE - NYC Rolling Sales

Projet réalisé par Ishak Karaaslan, Loïc Fontaine et Nathan Smeyers dans le cadre du cours de MLDE à Supinfo.

## Description

Le marché immobilier est une partie importante de l'économie mondiale, et la valeur du bien est un facteur crucial dans le processus de prise de décision des acheteurs et des vendeurs. Cependant, déterminer précisément la valeur d'un bien immobilier peut être un processus complexe et chronophage qui implique l'analyse d'un certain nombre de facteurs différents tels que l'emplacement, la taille, l'âge et les caractéristiques.
Ce projet vise à développer un modèle d'apprentissage automatique pour prédire la valeur d'un bien immobilier résidentiel.

## Données

Les données utilisées pour ce projet provient de [Kaggle](https://www.kaggle.com/datasets/new-york-city/nyc-property-sales?datasetId=2648).
Ce dataset est un enregistrement de chaque bâtiment ou unité de bâtiment (appartement, etc.) vendu sur le marché immobilier de New York City au cours d'une période de 12 mois.

## Validation des données

Pour la validation de nos données nous avons décidé d'utiliser great_expectations. Nous avons donc créé un script [python](/docker/mlflow/clean.py) qui permet de valider les données grâce à des expectations. Si les données ne sont pas validées, le script permet de les nettoyer et de les sauvegarder dans un fichier csv.

## Prefect


Pour orchestrer notre workflow nous avons décidé d'utiliser [Prefect](https://www.prefect.io/). Nous avons utilisé prefect dans notre [script principal](/docker/mlflow/main.py) il nous permet de lancer les différents scripts python qui permettent de nettoyer les données, de les valider, de les transformer et de les entraîner. 

## MLFlow

Pour le tracking de nos modèles nous avons décidé d'utiliser [MLFlow](https://mlflow.org/). MLflow nous permet de lancer l'entraînement de nos modèles et de les sauvegarder dans un dossier, de les comparer et de les déployer.

## API

Pour la création de notre API nous avons décidé d'utiliser [FastAPI](https://fastapi.tiangolo.com/). Nous avons donc créé un [script](/docker/api/main.py) qui permet de lancer notre API. Cette API permet de récupérer les données de notre modèle de production et de les utiliser pour fournir des informations a notre front-end et faire des prédictions.

## Docker 

Pour héberger nos différents services nous avons décidé d'utiliser [Docker](https://www.docker.com/). Nous avons donc créé un [docker-compose](/docker/docker-compose.yml) qui permet de lancer nos différents services. Nous avons décidé d'utiliser docker car il permet de lancer nos différents services en une seule commande et de les lancer dans différents conteneurs.

## Lancement du projet

Pour lancer le projet il suffit de lancer la commande suivante **dans le dossier docker** :

```bash
docker-compose up --build
```


Une fois le projet lancé, vous pouvez accéder à :
- Notre site de prédictions à l'adresse suivante : [http://localhost:3000](http://localhost:3000)
- La documentation de l'API à l'adresse suivante : [http://localhost:8000/docs](http://localhost:8000/docs)
- MLFlow à l'adresse suivante : [http://localhost:5001](http://localhost:5001)
- Prefect à l'adresse suivante : [http://localhost:4200](http://localhost:4200)

## Architecture du projet

Voici un schéma résumant l'architecture et le fonctionnement de notre projet : https://excalidraw.com/#json=fCLuQASpdTNbl--H_o1Mu,K53SowdgEOhTEIv0OeMr1Q






