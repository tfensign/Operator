from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db
from routes import auth, messages, checklists, send, integrations, webhooks
import config
import os

app = FastAPI(
    title="Operator",
    description="Privacy-first communication manager",
    version="0.1.0"
)

# Initialize database
init_db()

# CORS middleware
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://tfensign.github.io",
    "*"  # Allow all for development
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(checklists.router)
app.include_router(send.router)
app.include_router(integrations.router)
app.include_router(webhooks.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(static_dir, "static")), name="static")

    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT
    )
