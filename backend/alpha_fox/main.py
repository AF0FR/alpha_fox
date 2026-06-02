from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alpha_fox.api.routes.radio import router as radio_router
from alpha_fox.api.websocket.radio_status_ws import router as radio_status_ws_router
from alpha_fox.api.websocket.waterfall_ws import router as waterfall_ws_router
from alpha_fox.api.websocket.ping_ws import router as ping_ws_router

app = FastAPI(
    title="alpha_fox",
    description="Web-based rig control and waterfall dashboard.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "app": "alpha_fox",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "radio_status": "/radio/status",
        "radio_status_ws": "/ws/radio/status",
        "waterfall_ws": "/ws/waterfall",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": "alpha_fox",
    }


app.include_router(radio_router)
app.include_router(radio_status_ws_router)
app.include_router(waterfall_ws_router)
app.include_router(ping_ws_router)