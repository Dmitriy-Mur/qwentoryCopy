from fastapi import FastAPI

app = FastAPI(
    title="Warehouse Management API",
    description="Backend для АСУ складского учёта",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Warehouse API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }