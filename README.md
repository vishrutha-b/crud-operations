# FastAPI CRUD Backend with PostgreSQL

A production-ready REST API built with **FastAPI** + **PostgreSQL** for full CRUD operations on an **Items** resource.

---

## 📦 Project Structure

```
gitactions/
├── main.py           # App entry point
├── database.py       # DB engine & session
├── models.py         # SQLAlchemy ORM model
├── schemas.py        # Pydantic request/response schemas
├── crud.py           # Database CRUD functions
├── routers/
│   └── items.py      # API endpoints
├── requirements.txt
├── .env              # Your DB credentials (DO NOT COMMIT)
└── .env.example      # Template for .env
```

---

## ⚙️ Prerequisites

- Python 3.10+
- PostgreSQL installed + running via **pgAdmin**
- A database created (e.g. `crud_db`)

---

## 🚀 Setup

### 1. Create the PostgreSQL Database in pgAdmin

Open pgAdmin → right-click **Databases** → **Create** → **Database**  
Name it `crud_db` and save.

### 2. Configure your `.env`

Edit the `.env` file with your actual PostgreSQL credentials:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/crud_db
```

### 3. Create a virtual environment & install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

---

## 🔗 API Endpoints

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| GET    | `/`                    | Health check         |
| GET    | `/api/v1/items/`       | List all items       |
| GET    | `/api/v1/items/{id}`   | Get item by ID       |
| POST   | `/api/v1/items/`       | Create new item      |
| PUT    | `/api/v1/items/{id}`   | Update item (partial)|
| DELETE | `/api/v1/items/{id}`   | Delete item          |

### 📋 Interactive Docs

- Swagger UI → `http://127.0.0.1:8000/docs`
- ReDoc     → `http://127.0.0.1:8000/redoc`

---

## 📝 Sample Requests

### Create an Item
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "Gaming laptop", "price": 150000, "is_available": true}'
```

### Get All Items
```bash
curl http://127.0.0.1:8000/api/v1/items/
```

### Update an Item
```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/items/1" \
  -H "Content-Type: application/json" \
  -d '{"price": 120000, "is_available": false}'
```

### Delete an Item
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/items/1"
```
