import fastapi
from api.routes import router

APP = fastapi.FastAPI()
APP.include_router(router, prefix="/api", tags=["Flight Alerts"])