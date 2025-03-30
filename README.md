+++
# SkyAlert API

SkyAlert API est un projet conçu pour offrir des fonctionnalités météorologiques, y compris des notifications personnalisées basées sur des seuils définis par l'utilisateur.

## Team Members
- [Marheraroui Amin](https://github.com/aminmarh)
- [Ibouda Yasser](https://github.com/Yasser1080)
- [Souissi Dhia-Eddine](https://github.com/Dhia78)

---

## Prerequisites
Avant de commencer, assurez-vous d'avoir les outils suivants installés :
- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/)
- [Git](https://git-scm.com/)

---

## Technologies et Outils Utilisés

### **1. Backend**
- **Flask** : Framework web principal pour gérer les APIs et la logique backend.
- **Flask-JWT-Extended** : Pour la gestion des tokens JWT, sécurisant les endpoints.
- **Flask-Migrate** : Pour gérer les migrations de base de données.
- **Flask-SQLAlchemy** : ORM (Object Relational Mapping) utilisé pour interagir avec PostgreSQL.
- **Flasgger** : Pour générer automatiquement la documentation Swagger des APIs.
- **APScheduler** : Permet de planifier des tâches périodiques comme la comparaison des données météorologiques avec les seuils.

### **2. Base de Données**
- **PostgreSQL** : Base de données relationnelle utilisée pour stocker les utilisateurs, les villes favorites, les seuils et les notifications.

### **3. Notifications**
- **Fichier Notification Customisé** : Les notifications sont également stockées dans la base de données et récupérables via une API REST.

### **4. Structuration et Qualité**
- **Blueprints** : Organisation modulaire des routes (authentification, météo, seuils, notifications).
- **Swagger** : Documentation complète des APIs via `/apidocs/`.
- **Tests** : Structuré pour inclure des tests unitaires et d'intégration.
- **Flake8** et **Black** : Respect des standards de code Python.
- **Schemas Marshmallow** : Toutes les données saisies par les utilisateurs ou reçues d'une API sont validées et typées grâce à des schémas définis avec **Marshmallow**.

---

## Cloning the Project
Clonez ce projet en utilisant la commande suivante :

```bash
git clone git@github.com:aminmarh/SkyAlert-API.git
cd SkyAlert-API
```

---

## Fichier `.env`
Le projet utilise un fichier `.env` pour stocker les informations sensibles. Voici un exemple :

```
FLASK_APP=run.py
FLASK_ENV=development

SECRET_KEY=1629622497db43c04b60d9c88a4897c4f1a586ca8f04208aebf668b18fdaedce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=BH766zO7nof9eY
POSTGRES_DB=skyalert_db
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
JWT_SECRET_KEY=56295efc6e65be181e6225c580393f841d8830b15a83746e25f79007bc94fbd0
WEATHER_API_KEY=4a058a366a8142408b1122438241012

EMAIL_SENDER=nepasrepondre.skyalert@gmail.com
EMAIL_PASSWORD=vgbl vbbj iujb yklg
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

LOG_LEVEL=INFO
SCHEDULER_API_ENABLED=True
```

---

## Using Docker

### Étapes pour Exécuter le Projet avec Docker

**Docker lance automatiquement trois services :**
1. **Base de données PostgreSQL :**
   - Service `db` basé sur l'image PostgreSQL.
   - Accessible sur le port `5123`.
   - Utilise un volume local `./pData` pour la persistance des données.

2. **Application Backend :**
   - Service `app` qui exécute l'application Flask.
   - Disponible sur le port `5000`.
   - Dépend du service `db`.

3. **Adminer :**
   - Service `adminer` pour gérer facilement la base de données via une interface web.
   - Disponible sur le port `8080`.

**Construire les conteneurs :**

```bash
docker-compose build
```

**Démarrer les conteneurs :**

```bash
docker-compose up
```

**Accéder aux services :**
- **Application Backend :** [http://localhost:5000](http://localhost:5000)
- **Adminer :** [http://localhost:8080](http://localhost:8080)

---

## Tester l'application en entier

Pour tester l'application dans son intégralité, vous devez également cloner et exécuter le frontend associé au projet. Vous pouvez trouver le repository du frontend ici :  
[SkyAlert Frontend Repository](https://github.com/aminmarh/SkyAlert-UI)

Suivez les instructions fournies dans le fichier `README.md` du repository frontend pour configurer et exécuter le frontend. Une fois le frontend et le backend correctement configurés et démarrés, vous pourrez interagir avec l'application complète.

---
+++