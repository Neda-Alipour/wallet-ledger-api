# wallet-ledger-api
Fintech-style wallet and transaction ledger backend built with FastAPI, PostgreSQL, and Docker. Focused on data integrity, idempotency, and concurrency safety.


#  Wallet Ledger API

A production-inspired **Wallet & Ledger backend** built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy 2.0**.

This project demonstrates how modern fintech applications handle wallet balances using a **double-entry ledger** while ensuring **atomic transactions**, **idempotency**, and **data integrity**.

---

##  Features

-  User authentication
-  User registration & login
-  Automatic wallet creation
-  Deposit funds
-  Withdraw funds
-  Double-entry ledger
-  Transaction history
-  Atomic database transactions
-  Input validation with Pydantic
-  Session-based authentication
-  Alembic database migrations
-  SQLAlchemy 2.0 ORM

---

# Tech Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | Backend framework |
| PostgreSQL | Database |
| SQLAlchemy 2.0 | ORM |
| Alembic | Database migrations |
| Pydantic | Validation |
| Jinja2 | HTML templates |
| Passlib + bcrypt | Password hashing |
| Starlette Sessions | Session authentication |

---

# Project Structure

```
wallet-ledger-api/
│
├── alembic/
│   └── database migrations
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   └── wallet.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── wallet.py
│   │   ├── transaction.py
│   │   ├── ledger.py
│   │   └── idempotency.py
│   │
│   ├── schemas/
│   │   └── auth.py
│   │
│   ├── services/
│   │   └── auth.py
│   │
│   ├── templates/
│   ├── static/
│   └── main.py
│
├── requirements.txt
└── README.md
```

---

# Database Design

The application separates business events from accounting entries.

## User

Represents an authenticated user.

A user can own multiple wallets.

---

## Wallet

Stores:

- Currency
- Current balance
- Owner

---

## Transaction

Represents the business event.

Examples:

- Deposit
- Withdrawal

Transactions do **not** directly affect balances.

---

## Ledger Entry

Each transaction creates ledger entries that update wallet balances.

This design mirrors how real financial systems maintain an auditable history instead of simply modifying a balance field.

---

# Transaction Flow

Example: Deposit $100

```
User
   │
   ▼
POST /wallet/deposit
   │
   ▼
Create Transaction
   │
   ▼
Create Ledger Entry
   │
   ▼
Update Wallet Balance
   │
   ▼
Commit Transaction
```

All operations occur inside a single database transaction to guarantee consistency.

---

# Authentication

The application uses:

- Session-based authentication
- Secure password hashing (bcrypt)
- Server-side sessions
- Protected wallet routes

Unauthenticated users are redirected to the login page.

---

# Running Locally

## Clone

```bash
git clone https://github.com/Neda-Alipour/wallet-ledger-api.git
cd wallet-ledger-api
```

## Create virtual environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/wallet
SECRET_KEY=your-secret-key
```

## Run migrations

```bash
alembic upgrade head
```

## Start the application

```bash
uvicorn app.main:app --reload
```

Then visit:

```
http://127.0.0.1:8000
```

---

# Main Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /signup | Registration page |
| POST | /signup | Create user |
| GET | /login | Login page |
| POST | /login | Authenticate user |
| GET | /wallet | Wallet dashboard |
| POST | /wallet/deposit | Deposit funds |
| POST | /wallet/withdraw | Withdraw funds |

---

# Design Principles

This project focuses on backend engineering practices commonly used in fintech systems:

- Double-entry accounting concepts
- Atomic database transactions
- Separation of business events from ledger entries
- SQLAlchemy 2.0 patterns
- Pydantic validation
- Database migrations
- Layered project architecture
- Secure authentication
- Error handling and redirects

---

# Future Improvements

- REST API documentation
- JWT authentication
- Wallet-to-wallet transfers
- Pagination for transaction history
- Docker Compose setup
- Redis-powered idempotency
- Unit and integration tests
- CI/CD pipeline with GitHub Actions

---

# Learning Objectives

This project was built to deepen my understanding of:

- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic migrations
- Fintech ledger architecture
- Database transactions
- Session authentication
- Backend system design

---

## License

This project is licensed under the MIT License.
