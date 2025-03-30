+++
# SkyAlert API

SkyAlert API is a project designed to provide weather-related features, including personalized notifications based on user-defined thresholds.

## Team Members
- [Marheraroui Amin](https://github.com/aminmarh)
- [Ibouda Yasser](https://github.com/Yasser1080)
- [Souissi Dhia-Eddine](https://github.com/Dhia78)

---

## Prerequisites
Before getting started, make sure you have the following tools installed:
- [Python 3.9.6](https://www.python.org/downloads/release/python-396/)
- [Docker](https://www.docker.com/)
- [Git](https://git-scm.com/)

---

## Technologies & Tools Used

### **1. Backend**
- **Flask**: Main web framework used to manage APIs and backend logic.
- **Flask-JWT-Extended**: Handles JWT token management and secures endpoints.
- **Flask-Migrate**: Manages database migrations.
- **Flask-SQLAlchemy**: ORM used to interact with PostgreSQL.
- **Flasgger**: Automatically generates Swagger API documentation.
- **APScheduler**: Schedules periodic tasks such as comparing weather data with user thresholds.

### **2. Database**
- **PostgreSQL**: Relational database used to store users, favorite cities, thresholds, and notifications.

### **3. Notifications**
- **Custom Notification File**: Notifications are stored in the database and can be retrieved via REST API.

### **4. Structure & Code Quality**
- **Blueprints**: Modular route organization (auth, weather, thresholds, notifications).
- **Swagger**: Full API documentation available at `/apidocs/`.
- **Flake8** and **Black**: Code formatting and linting tools.
- **Marshmallow Schemas**: All data input by users or received from external APIs is validated and typed using **Marshmallow**.
- **Tests**: Structured to include both unit and integration tests.

---

## Cloning the Project

Clone this repository with the following command:

```bash
git clone git@github.com:aminmarh/SkyAlert-API.git
cd SkyAlert-API
```

---

## `.env` File

The project uses a `.env` file to store sensitive information. Here's an example:

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

### Steps to Run the Project with Docker

**Docker launches three services automatically:**

1. **PostgreSQL Database:**
   - Service `db` based on the official PostgreSQL image.
   - Exposed on port `5123`.
   - Uses local volume `./pData` for data persistence.

2. **Backend Application:**
   - Service `app` that runs the Flask backend.
   - Exposed on port `5000`.
   - Depends on the `db` service.

3. **Adminer:**
   - Service `adminer` provides a user interface to interact with the database.
   - Exposed on port `8080`.

**Build and run the containers:**

```bash
docker-compose up --build
```

**Access the services:**
- **Backend API:** [http://localhost:5000/apidocs](http://localhost:5000/apidocs)
- **Adminer UI:** [http://localhost:8080](http://localhost:8080)

---

## Full App Testing

To test the full application, you also need to clone and run the frontend project. You can find the frontend repository here:  
[SkyAlert Frontend Repository](https://github.com/aminmarh/SkyAlert-UI)

Follow the instructions in the `README.md` file of the frontend repository to set it up and run it. Once both frontend and backend are up and running, you'll be able to interact with the complete application.

---