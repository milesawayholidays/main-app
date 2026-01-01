import os

import fastapi
from fastapi import Depends
from fastapi.staticfiles import StaticFiles
from backend_api.router import router
from backend_api.dependencies import ensure_request_initialized

APP = fastapi.FastAPI()
APP.include_router(
	router,
	prefix="/api",
	tags=["Flight Alerts"],
	dependencies=[Depends(ensure_request_initialized)],
)

if os.path.isdir("public"):
	APP.mount("/public", StaticFiles(directory="public"), name="root")