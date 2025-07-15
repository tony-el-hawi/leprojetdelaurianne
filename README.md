# Démarrage des services avec Docker Compose

Ce projet utilise Docker Compose pour lancer simultanément l'API et le site web.

## Lancement des services

À la racine du projet, exécutez :

```sh
docker-compose up --build
```

## Accès aux services

- **API** :
  - Swagger disponible sur : [http://localhost:5000/swagger](http://localhost:5000/docs)
- **Site web** :
  - Interface disponible sur : [http://localhost:8080](http://localhost:8080)

## Arrêt des services

```sh
docker-compose down
```


## Initialisation de la base de données

Avant de démarrer les services, il est recommandé d'exécuter les scripts d'importation pour remplir la base de données :

```sh
pip install requests
python .\api\tools\import-db-items-json.py
python .\api\tools\import-db-orders-json.py
```

for mac
```sh
pip3 install requests
python3 ./api/tools/import-db-items-json.py
```

Cela permet d'ajouter les données nécessaires dans la base SQLite.

---

Assurez-vous que Docker et Docker Compose sont installés sur votre machine.
