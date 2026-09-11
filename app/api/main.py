from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="PhotoAgent API",
    description="Local-first AI photo management API",
    version="1.0.0",
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "PhotoAgent",
        "status": "running",
    }