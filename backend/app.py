from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import auth, messages, checklists, send, integrations, webhooks
import config

app = FastAPI(
    title="Operator",
    description="Privacy-first communication manager",
    version="0.1.0"
)

# Initialize database
try:
    init_db()
except Exception as e:
    print(f"Database initialization error: {e}")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT
    )
