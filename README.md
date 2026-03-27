# Discover Rwanda Setup Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis (optional — for WebSocket session tracking)
- Docker Desktop (optional, for one-command startup)

---

## Quickstart with Docker (recommended for demo)

This repo now includes a full Docker setup for frontend + backend + MySQL + Redis.

From the project root:
```bash
docker compose up --build
```

After startup:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- MySQL: localhost:3306 (user: `dr_user`, pass: `dr_pass`, db: `discover_rwanda`)

Notes:
- The API container waits for MySQL, runs `alembic upgrade head`, then seeds demo data.
- Seeding is enabled by default (`AUTO_SEED=true`) and resets demo data on each start.
- To keep existing data, set `AUTO_SEED=false` in `docker-compose.yml`.

---

## Deploy on Render (Web Services, no Redis)

This repo includes a `render.yaml` for two Render web services:
- API: `discover_Rwanda-main/server`
- Client: `discover_Rwanda-main/client`

### Backend (API) required settings
- Use your external MySQL (for example Aiven) in `DATABASE_URL`.
- Set `SECRET_KEY` to a strong random string.
- Set `ALLOWED_ORIGINS` to your Render client URL(s), comma-separated.
- Keep `AUTO_MIGRATE=true`.
- For production, keep `AUTO_SEED=false`.

### Frontend (Client) required settings
- Set `VITE_BACKEND_TARGET` to your API Render URL, for example:
  - `https://discover-rwanda-api.onrender.com`

Notes:
- Redis is not required for this deployment path.
- The API container now honors Render's `PORT` automatically.

---

## 1. Clone / unzip the project

```
discover-rwanda/
├── server/      ← FastAPI backend
└── client/      ← React frontend
```

---

## 2. Database setup

```sql
-- In MySQL
CREATE DATABASE discover_rwanda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dr_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON discover_rwanda.* TO 'dr_user'@'localhost';
FLUSH PRIVILEGES;
```

You can create the database automatically (idempotent) with the script below, which will print `Database already exists` if it is present.

Run from the `server` folder:
```powershell
cp .env.example .env   # if needed
python scripts/create_db_if_missing.py
```


---

## 3. Backend setup

```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — update DB_PASSWORD and DATABASE_URL with your MySQL credentials

# Run database migrations
alembic upgrade head

# Seed with demo data
python scripts/seed.py

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API is now running at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc

---

## 4. Frontend setup

```bash
cd client

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend is now running at: http://localhost:3000

---

## 5. Demo accounts (seeded automatically)

| Role     | Email                          | Password        |
|----------|-------------------------------|-----------------|
| Admin    | admin@discoverrwanda.com       | Admin@1234      |
| Faculty  | faculty@alu.edu                | Faculty@1234    |
| Student  | alice@example.com              | Student@1234    |
| Student  | bob@example.com                | Student@1234    |
| Business | kigali@safarilodge.rw          | Business@1234   |
| Business | info@visitrwanda.rw            | Business@1234   |
| Mentor   | mentor1@tourismtech.rw         | Mentor@1234     |

---

## 6. Core user flows to test

### Student flow
1. Log in as `alice@example.com`
2. **Dashboard** → See matched challenges and learning progress
3. **Challenges → My matches** → View weighted match scores
4. Open a challenge → Create a team or join an existing one
5. **Projects** → Open the project workspace → Add tasks, milestones, use chat
6. **Learning** → Enroll in a path → Complete lessons + quiz → Earn badge
7. **Mentors** → Book a session
8. **Portfolio** → See auto-populated projects, skills, badges

### Business flow
1. Log in as `kigali@safarilodge.rw`
2. **Dashboard** → See your challenges and team status
3. **Challenges** → Post a new challenge (requires approved verification)
4. Open a challenge → Monitor teams and project progress

### Admin flow
1. Log in as `admin@discoverrwanda.com`
2. **Admin** → Overview analytics
3. **Pending tab** → Approve or reject submitted challenges
4. **Verifications tab** → Approve business accounts
5. **Users tab** → Manage all platform users

---

## 7. API documentation

FastAPI auto-generates full interactive docs.  
Visit: **http://localhost:8000/docs**

All endpoints are under `/api/v1/`.  
Click "Authorize" and enter your JWT token (get it from the `/api/v1/auth/login` endpoint).

---

## 8. WebSocket chat

Project workspaces have real-time chat via WebSocket.  
Connection URL: `ws://localhost:8000/ws/projects/{project_id}?token={jwt_token}`

---

## 9. Environment variables reference

| Variable                  | Description                          | Default              |
|---------------------------|--------------------------------------|----------------------|
| SECRET_KEY                | JWT signing key (min 32 chars)       | (dev key)            |
| DATABASE_URL              | MySQL connection string              | localhost/discover_rwanda |
| DB_PASSWORD               | MySQL password                       | —                    |
| REDIS_URL                 | Redis for WebSocket sessions         | redis://localhost:6379 |
| UPLOAD_DIR                | Local file upload directory          | uploads/             |
| ALLOWED_ORIGINS           | CORS origins (comma-separated)       | localhost:3000,5173  |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT access token lifetime          | 60                   |

---

## 10. Production notes

- Set `DEBUG=false` in `.env`
- Use a proper `SECRET_KEY` (generate with `openssl rand -hex 32`)
- Run behind nginx with SSL (TLS 1.3)
- Use `gunicorn` with `uvicorn` workers: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
- Enable Redis for WebSocket state sharing across workers
- Run `alembic upgrade head` on every deployment
- Use a managed MySQL service (PlanetScale, RDS, etc.) for production
