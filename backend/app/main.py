from fastapi import FastAPI

app = FastAPI(title="MadWorld API", version="0.1.0")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "madworld-api"}

@app.get("/api/v1/world")
def world() -> dict:
    return {
        "season": 1,
        "tick": 0,
        "regions": [
            {"id": "dust_basin", "name": "Dust Basin", "security": "lawless"},
            {"id": "iron_ruins", "name": "Iron Ruins", "security": "contested"},
            {"id": "salt_coast", "name": "Salt Coast", "security": "frontier"},
        ],
    }
