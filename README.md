# Wallet Ledger

A full-stack digital wallet and transaction ledger system built with **FastAPI, PostgreSQL, Redis, SQLAlchemy, and React**.

The project simulates the core backend architecture of a financial wallet system, including user authentication, multi-currency wallets, deposits, withdrawals, cross-user transfers, transaction history, and double-entry ledger records.

> Built as a backend-focused portfolio project to explore real-world financial application architecture, transactional integrity, authentication, database design, and API development.

## Quick Start

### Prerequisites

Make sure you have installed:

* Python 3.11+
* PostgreSQL
* Redis
* Node.js and npm

### 1. Clone the repository

```bash
git clone https://github.com/Neda-Alipour/wallet-ledger-api.git
cd wallet-ledger-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/wallet_ledger

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start Redis

Make sure your Redis server is running.

### 7. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

### 8. Start the React frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at the URL provided by Vite.

## Project Goals

This project was designed to demonstrate practical backend engineering concepts beyond basic CRUD operations.

The main goals were to:

* Design a realistic relational database for a financial application
* Implement secure user authentication using JWT
* Use Redis for JWT token revocation
* Model multi-currency wallets
* Implement deposits, withdrawals, and cross-user transfers
* Maintain transaction history using a double-entry ledger structure
* Preserve financial data integrity through database transactions
* Use atomic database-level balance updates
* Separate API routes, business logic, schemas, and database models
* Implement database migrations with Alembic
* Build a React frontend that consumes the FastAPI API
* Apply validation and meaningful HTTP error handling
* Create an architecture that can be extended with more advanced financial features

## Features

### Authentication and Security

* User registration and login
* Secure password hashing with bcrypt
* JWT-based authentication
* JWT expiration handling
* Redis-backed token blacklist for logout and token revocation
* Protected API endpoints
* Email normalization
* Duplicate email detection
* Environment-based configuration for secrets and database credentials

### Multi-Currency Wallets

Each user can have a separate wallet for each supported currency.

Currently supported:

* USD
* EUR
* GBP

New users automatically receive their default currency wallets with an initial balance of `0.00`.

The architecture follows the rule that a user has **one wallet per currency**, rather than storing multiple currencies inside a single wallet.

### Financial Operations

The system supports three core transaction types:

#### Deposit

Adds funds to a user's wallet and creates a corresponding ledger entry.

#### Withdrawal

Removes funds from a wallet while preventing withdrawals that exceed the available balance.

The balance update is performed atomically at the database level:

```text
balance >= withdrawal_amount
```

This prevents the application from reducing a wallet below zero.

#### Transfer

Transfers funds between **two different users' wallets**.

A transfer:

1. Validates the authenticated user's source wallet
2. Retrieves the destination wallet
3. Verifies both wallets use the same currency
4. Checks sufficient source balance
5. Decreases the source balance
6. Increases the destination balance
7. Creates a single transaction record
8. Creates two corresponding ledger entries
9. Commits the complete operation as one database transaction

This models a more realistic financial transfer than simply changing one balance.

## Double-Entry Ledger Design

One of the core concepts of the project is separating **transactions** from **ledger entries**.

A `Transaction` represents the business event.

A `LedgerEntry` represents the effect that transaction had on a specific wallet.

For example, transferring `$100` from Alice to Bob creates:

```text
Transaction
└── TRANSFER $100
    │
    ├── Ledger Entry
    │   └── Alice Wallet: -$100
    │
    └── Ledger Entry
        └── Bob Wallet: +$100
```

This allows a single transaction to affect multiple wallets while maintaining an auditable history of each wallet's individual balance changes.

Instead of storing only the final wallet balance, the system keeps a record of **how that balance changed**.

This provides a foundation for future features such as:

* Auditing
* Transaction reconciliation
* Balance history
* Financial reporting
* Transaction reversals
* Transaction metadata

## Transactional Integrity

Financial operations are handled with database transactions.

For example, a transfer must not result in:

```text
Source wallet:   -$100
Destination:     unchanged
```

or:

```text
Source wallet:   unchanged
Destination:     +$100
```

The source balance update, destination balance update, transaction creation, and ledger entries are committed together.

If an exception occurs, the database session is rolled back.

```text
Transfer Request
      |
      v
Validate
      |
      v
Create Transaction
      |
      +-- Decrease Source
      |
      +-- Increase Destination
      |
      +-- Create Source Ledger Entry
      |
      +-- Create Destination Ledger Entry
      |
      v
    COMMIT
```

This provides atomicity for the core financial operations.

## Business Rules and Validation

The API enforces several important wallet rules:

* Transaction amounts must be greater than zero
* Amounts use decimal precision suitable for monetary values
* A wallet cannot be withdrawn below its available balance
* Source and destination wallets must be different
* Transfer wallets must use the same currency
* Users can only perform operations on wallets they own
* Transaction references are unique
* Missing wallets return appropriate `404` responses
* Duplicate transaction references return `409 Conflict`
* Invalid authentication returns `401 Unauthorized`
* Invalid financial operations return meaningful HTTP errors

Request validation is handled through Pydantic and FastAPI.

## Architecture

The backend follows a layered architecture instead of placing all business logic directly inside API routes.

```text
+------------------------------+
|          React UI            |
+---------------+--------------+
                | HTTP / REST
                v
+------------------------------+
|       FastAPI Routers        |
|   Authentication / Wallet    |
+---------------+--------------+
                |
                v
+------------------------------+
|        Service Layer         |
| Auth / Wallet / Transaction  |
+---------------+--------------+
                |
         +------+-------+
         |              |
         v              v
+---------------+ +---------------+
|  PostgreSQL   | |     Redis     |
|               | |               |
| Users         | | JWT           |
| Wallets       | | blacklist     |
| Transactions  | |               |
| Ledger        | |               |
+---------------+ +---------------+
```

### Backend layers

**API layer**

Handles HTTP requests, responses, authentication dependencies, and status codes.

**Service layer**

Contains business logic for authentication, wallet management, deposits, withdrawals, transfers, and transaction history.

**Schema layer**

Uses Pydantic models for request validation and response serialization.

**Model layer**

Uses SQLAlchemy ORM models to represent the PostgreSQL database.

**Database layer**

Provides SQLAlchemy sessions and Redis connectivity.

## Database Design

The PostgreSQL database is built around four primary entities:

```text
Users
  |
  | 1:N
  v
Wallets
  |
  | 1:N
  v
Ledger Entries
  |
  | N:1
  v
Transactions
```

### Users

Stores:

* UUID
* Email
* Hashed password
* Active status
* Creation timestamp

### Wallets

Stores:

* UUID
* User relationship
* Currency
* Decimal balance
* Creation timestamp

### Transactions

Stores:

* UUID
* Transaction type
* Status
* Unique reference
* Creation timestamp

Supported transaction types:

```text
deposit
withdrawal
transfer
```

### Ledger Entries

Stores:

* UUID
* Wallet relationship
* Transaction relationship
* Signed amount
* Creation timestamp

The signed amount represents both increases and decreases:

```text
+100.00 → credit
-100.00 → debit
```

## UUID-Based Identifiers

The system uses UUIDs for users, wallets, transactions, and ledger entries.

This avoids relying on predictable sequential identifiers and provides identifiers that are better suited to distributed applications and public APIs.

## Efficient Database Operations

Wallet balance changes use SQL-level updates rather than:

```text
SELECT balance
|
calculate new balance in Python
|
UPDATE balance
```

For withdrawals, the update includes the balance constraint directly:

```text
UPDATE wallets
SET balance = balance - amount
WHERE id = wallet_id
AND balance >= amount
```

This makes the insufficient-balance check part of the database operation itself.

The application then checks whether the update affected a wallet.

This is particularly important for financial operations where concurrent requests can otherwise introduce race conditions.

## Idempotency Foundation

The database schema includes an `idempotency_keys` table designed to support idempotent financial operations.

This provides a foundation for preventing duplicate processing when clients retry requests because of network failures or timeouts.

The current API does not yet apply idempotency keys to the transaction endpoints, leaving this as an extension point for future development.

## REST API

### Authentication

| Method | Endpoint       | Description                  |
| ------ | -------------- | ---------------------------- |
| `POST` | `/auth/signup` | Register a new user          |
| `POST` | `/auth/login`  | Authenticate and receive JWT |
| `GET`  | `/auth/logout` | Revoke the current JWT       |

### Wallets

| Method | Endpoint               | Description                    |
| ------ | ---------------------- | ------------------------------ |
| `GET`  | `/wallet/`             | Get user's wallets             |
| `GET`  | `/wallet/transactions` | Get wallet transaction history |
| `POST` | `/wallet/deposit`      | Deposit funds                  |
| `POST` | `/wallet/withdraw`     | Withdraw funds                 |
| `POST` | `/wallet/transfer`     | Transfer funds between wallets |

## React Frontend

The project includes a React frontend built with:

* React 19
* Vite
* React Router
* Axios
* JavaScript
* CSS

The frontend provides a user-facing interface for interacting with the wallet API.

### Frontend functionality

* User registration
* Login/logout
* Protected routes
* Dashboard
* Wallet overview
* Multi-currency wallet cards
* Deposit interface
* Withdrawal interface
* Transfers
* Transaction history
* Ledger view
* Profile page
* Loading states
* Error states
* Empty states
* Currency and date formatting
* Wallet ID copying
* Centralized Axios API client

The frontend communicates with the FastAPI backend through a dedicated API layer and automatically attaches JWT authentication tokens to protected requests.

## API Documentation

FastAPI automatically generates an OpenAPI specification for the API.

The project also includes a Scalar API reference available at:

```text
/scalar
```

This provides an interactive interface for exploring and testing the API.

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy 2.0
* Pydantic
* PostgreSQL
* Redis
* Alembic
* JWT
* Passlib
* bcrypt
* Uvicorn

### Frontend

* React
* Vite
* React Router
* Axios
* JavaScript
* CSS

### Development

* Git
* Pytest
* Alembic migrations
* Environment-based configuration

## Project Structure

```text
wallet-ledger-api/
|
├── app/
│   ├── api/
│   │   ├── router.py
│   │   └── routers/
│   │       ├── auth.py
│   │       └── wallet.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── redis_db.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── wallet.py
│   │   ├── transaction.py
│   │   ├── ledger.py
│   │   └── idempotency.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── wallet.py
│   │   └── transaction.py
│   │
│   ├── services/
│   │   ├── auth.py
│   │   ├── wallet.py
│   │   └── transaction.py
│   │
│   ├── main.py
│   └── utils.py
│
├── alembic/
│   └── versions/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
│
├── tests/
├── requirements.txt
├── alembic.ini
└── README.md
```

## Example Transfer

Suppose:

```text
Alice
USD Wallet
Balance: $500

Bob
USD Wallet
Balance: $100
```

Alice transfers `$150` to Bob.

The resulting state becomes:

```text
Alice: $350
Bob:   $250
```

The database records:

```text
Transaction
    type: transfer
    amount: $150

Ledger Entry #1
    wallet: Alice
    amount: -$150

Ledger Entry #2
    wallet: Bob
    amount: +$150
```

Both wallet updates and both ledger entries are committed as part of the same database transaction.

## Future Improvements

Potential future improvements include:

* Request-level idempotency for financial endpoints
* Transaction pagination
* Advanced transaction filtering
* Transaction reversal and refund support
* Wallet-to-wallet transfer references
* Audit logging
* Automated reconciliation
* More comprehensive automated tests
* Dockerized development environment
* CI/CD pipeline
* Rate limiting
* Refresh-token authentication
* Role-based authorization
* Additional currencies

## Project Status

The core wallet, transaction, authentication, ledger, and React frontend functionality is implemented.

The project is primarily intended as a portfolio and learning project demonstrating real-world backend architecture and financial transaction modeling.

## Author

**Neda Alipour**

Backend Developer | Python | FastAPI | SQL | PostgreSQL

[GitHub](https://github.com/Neda-Alipour)

[Portfolio](https://neda-alipour.github.io)
