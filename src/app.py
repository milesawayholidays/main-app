import fastapi
from fastapi.staticfiles import StaticFiles
from backend_api.router import router

APP = fastapi.FastAPI()
APP.include_router(router, prefix="/api", tags=["Flight Alerts"])
APP.mount("/public", StaticFiles(directory="public"), name="root")