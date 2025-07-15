# Instructions pour lancer l'API Flask localement

1. Installez les dépendances :
   ```powershell
   pip install -r requirements.txt
   ```

2. Lancez le serveur Flask :
   ```powershell
   python app/main.py
   ```

   > Lors du premier démarrage, la base SQLite (`database.sqlite3`) sera automatiquement créée si elle n'existe pas, avec le bon schéma.

3. Accédez à la documentation Swagger/OpenAPI :
   Ouvrez http://localhost:5000/swagger/ dans votre navigateur.

---
Ce projet ne dépend plus d'AWS ou de Terraform. Toute la logique API doit être développée dans `app/main.py` et les modules Python locaux. La persistance des données se fait dans une base SQL locale (SQLite par défaut).
