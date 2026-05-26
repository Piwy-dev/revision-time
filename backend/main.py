from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from backend.database import init_db
from backend.routes import router
import os

app = FastAPI(title="Study Tracker")

# Initialize database
init_db()

# Include API routes
app.include_router(router)

# Health endpoint
@app.get("/api/health")
def health():
    return {"status": "ok"}

# Serve static frontend files
frontend_path = Path("frontend/dist")

if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {"message": "Frontend not built. Run: cd frontend && pnpm run build"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
