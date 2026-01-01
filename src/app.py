import os

import fastapi
from fastapi import Depends
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope
from backend_api.router import router
from backend_api.dependencies import ensure_request_initialized

_FRONTEND_DIST = os.path.join("frontend", "dist")


class SPAStaticFiles(StaticFiles):
	async def get_response(self, path: str, scope: Scope) -> Response:
		response = await super().get_response(path, scope)
		if response.status_code == 404 and not scope.get("path", "").startswith("/api"):
			return await super().get_response("index.html", scope)
		return response

APP = fastapi.FastAPI()
APP.include_router(
	router,
	prefix="/api",
	tags=["Flight Alerts"],
	dependencies=[Depends(ensure_request_initialized)],
)


if os.path.isdir(_FRONTEND_DIST):
	# Serve the built frontend at `/`.
	APP.mount("/", SPAStaticFiles(directory=_FRONTEND_DIST, html=True), name="frontend")

elif os.path.isdir("public"):
	APP.mount("/public", StaticFiles(directory="public"), name="public")