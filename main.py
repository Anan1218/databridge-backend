from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import report, events, posts
from app.scheduler import start_scheduler

app = FastAPI(
    title="ProspectAI API",
    description="Backend API for ProspectAI application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from endpoints modules
app.include_router(posts.router)

@app.on_event("startup")
def on_startup():
    start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)