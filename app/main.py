from fastapi import FastAPI

app = FastAPI(title="Wallet Ledger API", version="1.0.0")

@app.get("/")
def health_check():
    return {"status": "Wallet Ledger API is running"}