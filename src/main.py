from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router


app = FastAPI(title="Deep Research Agent System")


def configure_middleware(app: FastAPI) -> None:
    """Registers the middleware required by the API service"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routes(app: FastAPI) -> None:
    """Serve static assets and attach the API routes"""
    app.include_router(router)
    app.mount("/static", StaticFiles(directory="static"), name="static")


configure_middleware(app)
configure_routes(app)


@app.get("/")
async def root() -> FileResponse:
    """Return the frontend entry page"""
    return FileResponse("static/index.html")