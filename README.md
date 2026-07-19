# Apexafrika-backend#  ApexAfrika

**The Peak of African Gaming**

ApexAfrika is a **Game Operations & Community Platform for African Esports** — a vertical SaaS platform designed to empower tournament organizers, players, gaming communities, and content creators across Africa.

---

##  Problem We Solve

African esports lacks:

* Structured tournament infrastructure
* Monetization systems (especially local payments like M-Pesa)
* Community-driven engagement tools
* Data & analytics for players and organizers

**ApexAfrika solves this by providing a unified platform for managing, playing, monetizing, and growing esports ecosystems.**

---

##  Features (19 Apps)

*  Tournament Management
*  Player Analytics
*  Community
*  Payments (M-Pesa)
*  Notifications
*  Chat (Real-time)
*  AI (Groq Integration)
*  Teams
*  Achievements
*  Schedules
*  Streaming
*  Content & Education
*  Newsletter
*  Feedback
*  Audit Logs
*  Legal (Terms, Privacy)
*  Authentication (JWT + OAuth + 2FA)

---

##  Tech Stack

| Layer      | Technology                          |
| ---------- | ----------------------------------- |
| Backend    | Django 5.1.4, Django REST Framework |
| Database   | PostgreSQL 15+                      |
| Cache      | Redis 7+                            |
| Queue      | Celery 5.4+                         |
| Auth       | JWT, Google OAuth, 2FA              |
| AI         | Groq (LLaMA 3)                      |
| Payments   | M-Pesa Daraja API                   |
| Deployment | Docker, Render                      |

---

##  Prerequisites

* Python 3.12+
* PostgreSQL 15+
* Redis 7+
* Docker (optional)
* Node.js 20+ (frontend)

---

##  Quick Start

```bash
git clone https://github.com/yourusername/apexafrika.git
cd apexafrika

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
```

---

##  Installation (Detailed)

### PostgreSQL Setup

```bash
sudo -u postgres psql
CREATE DATABASE apexafrika;
CREATE USER apexuser WITH PASSWORD 'password';
ALTER ROLE apexuser SET client_encoding TO 'utf8';
ALTER ROLE apexuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE apexuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE apexafrika TO apexuser;
```

### Redis Setup

```bash
sudo apt install redis
redis-server
```

### Environment Variables

```env
DEBUG=True
DJANGO_SECRET_KEY=your_secret
DB_NAME=apexafrika
DB_USER=apexuser
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

---

##  Docker Setup

```bash
docker-compose up --build
```

Run migrations:

```bash
docker-compose exec web python manage.py migrate
```

Create superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

##  API Documentation

| Endpoint             | Method   | Description        |
| -------------------- | -------- | ------------------ |
| /api/auth/register   | POST     | Register user      |
| /api/auth/login      | POST     | Login              |
| /api/tournaments     | GET/POST | Manage tournaments |
| /api/payments/mpesa  | POST     | Initiate payment   |
| /api/community/posts | GET/POST | Posts              |

###  Auth Flow

1. Login → Receive JWT
2. Send `Authorization: Bearer <token>`
3. Optional 2FA verification
4. OAuth via Google

---

##  Project Structure

```bash
apexafrika/
├── apps/
│   ├── users/
│   ├── tournaments/
│   ├── players/
│   ├── analytics/
│   ├── payments/
│   └── ...
├── core/
├── config/
├── requirements.txt
├── docker-compose.yml
└── manage.py
```

---

##  Development

* Use PEP8
* Use meaningful commit messages:

  * feat:
  * fix:
  * refactor:
* Run tests:

```bash
python manage.py test
```

---

##  Deployment (Render)

1. Create Web Service
2. Add environment variables
3. Connect PostgreSQL
4. Deploy

Health Check:

```
/api/health
```

---

##  Contributing

1. Fork repo
2. Create branch
3. Commit changes
4. Open PR

---

##  License

Proprietary / Commercial License

---

## Acknowledgments

* Safaricom (M-Pesa)
* African Gaming Community
* All Contributors
