from fastapi import FastAPI

app = FastAPI(
    title="Server Automation Sample API",
    version="1.0.0",
    description="Laboratory API for Ansible and Docker Compose validation.",
)


@app.get("/")
async def root():
    return {
        "application": "Server Automation Sample API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }
