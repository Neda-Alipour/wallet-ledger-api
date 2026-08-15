# Wallet Ledger API - React Frontend

A clean, modern, and production-ready React frontend for the **Wallet Ledger API** FastAPI backend. Built with Vite, React Router, Axios, and Vanilla CSS.

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
Open a terminal in the `frontend` directory and run:
```bash
npm install
```

### 2. Configure Environment Variables
Copy `.env.example` to create `.env`:
```bash
cp .env.example .env
```
Ensure the API base URL points to your running FastAPI backend server:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server
Run the Vite development server:
```bash
npm run dev
```
The application will open at: **`http://localhost:5173`**

---

## 📁 Project Structure

```text
frontend/
├── .env.example             # Template for environment variables
├── .env                     # Local environment variables (do not commit)
├── package.json             # Project dependencies & scripts
├── vite.config.js           # Vite configuration
├── index.html               # Main HTML entry document
└── src/
    ├── api/
    │   └── api.js           # Central API client & FastAPI REST calls
    ├── context/
    │   └── AuthContext.jsx  # Authentication state & session manager
    ├── components/
    │   ├── Layout.jsx       # Main layout wrapper (Header + Sidebar)
    │   ├── Header.jsx       # App bar with user info & logout button
    │   ├── Sidebar.jsx      # Navigation links menu
    │   ├── WalletCard.jsx   # Wallet display card with balance & ID copy
    │   ├── TransactionTable.jsx # Transaction history table
    │   ├── Loading.jsx      # Loading spinner state
    │   ├── ErrorMessage.jsx # Error banner component
    │   └── EmptyState.jsx   # Clean empty state message
    ├── pages/
    │   ├── Login.jsx        # User login form
    │   ├── Register.jsx     # User registration form
    │   ├── Dashboard.jsx    # Overview of balances & recent activity
    │   ├── Wallets.jsx      # Manage wallets + Deposit & Withdraw modals
    │   ├── Transfer.jsx     # Transfer funds between wallets
    │   ├── Transactions.jsx # Filtered transaction history log
    │   ├── Ledger.jsx       # Double-entry credit/debit audit view
    │   └── Profile.jsx      # User account & wallet overview
    ├── utils/
    │   ├── formatters.js    # Currency, Date, & ID formatting functions
    │   └── jwt.js           # Lightweight JWT payload decoder
    ├── App.jsx              # Application router & route guards
    ├── main.jsx             # React DOM root entrypoint
    └── index.css            # Global CSS styling & design system tokens
```

---

## 🔗 How Frontend & Backend Communicate

1. **Base API Layer (`src/api/api.js`)**: All HTTP request logic is isolated in `src/api/api.js` using Axios.
2. **Authentication Headers**: An Axios request interceptor automatically attaches the JWT token from `localStorage` into the header:
   ```text
   Authorization: Bearer <your_jwt_token>
   ```
3. **Form Encoding**: The `/auth/login` endpoint expects `application/x-www-form-urlencoded` per OAuth2 standard, which is automatically handled in `loginApi()`.

---

## 🔐 How Authentication Works

- **State Management**: Authentication state is stored in `AuthContext.jsx` (`src/context/AuthContext.jsx`).
- **Persistence**: Upon successful login, the JWT access token is stored in `localStorage`.
- **Session Restoration**: When the user reloads the app, `AuthContext` decodes the token claims and verifies validity with the backend.
- **Route Guards**:
  - `ProtectedRoute`: Prevents unauthenticated users from reaching `/dashboard`, `/wallets`, `/transfer`, `/transactions`, `/ledger`, or `/profile`.
  - `PublicOnlyRoute`: Prevents logged-in users from seeing the `/login` or `/register` pages unnecessarily.

---

## 🌐 Changing the API Base URL

If your FastAPI backend runs on a different port or host (e.g. `http://127.0.0.1:8000` or a remote server URL), edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📦 Building for Production

To compile static assets for production deployment:
```bash
npm run build
```
The production bundle will be generated in the `frontend/dist` folder.
