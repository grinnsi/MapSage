from contextlib import asynccontextmanager
import os, time, logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware

from server.database.db import Database
import server.ogc_apis.features.main as features_api
from server.config import get_logger_config
from server.ogc_apis.route_config import API_ROUTE, FEATURES_ROUTE

_LOGGER = logging.getLogger("server.api")

def init_main_api_server() -> FastAPI:
    # Initialize SQLite database after startup of FastAPI server
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _LOGGER.info("Starting FastAPI server")
        
        # Set uvicorn access logging to error if not in debug mode
        if os.getenv("APP_DEBUG_MODE", "False") == "False":
            logger = logging.getLogger("uvicorn.access")
            logger.setLevel(logging.ERROR)
        
        Database.init_sqlite_db(False)
        yield
        _LOGGER.info("Stopping FastAPI server")
    
    app = FastAPI(
        title="Implementation for the new OGC APIs",
        description="This server implements the new OGC APIs. Currently, it implements the OGC API - Features - Part 1 and Part 2: Core and CRS standard. Others will be added in the future.",
        version="1.0.0",
        lifespan=lifespan,
        root_path=os.getenv("API_SERVER_ROOT_PATH", "/"),
        openapi_url=f"{API_ROUTE}.json",
        docs_url=f"{API_ROUTE}.html",
        redoc_url=None,
    )
    
    @app.get("/")
    def get_subapplications(request: Request):
        return [
            {
                "title": "Implementation for the new OGC APIs",
                "description": "This server implements the new OGC APIs. Currently, it implements the OGC API - Features - Part 1 and Part 2: Core and CRS standard. Others will be added in the future.",
                "links:": [
                    {
                        "href": str(request.url).rstrip("/"),
                        "rel": "self",
                        "type": "application/json",
                        "title": "This document" 
                    },
                    {
                        "href": str(request.url).rstrip("/") + FEATURES_ROUTE,
                        "rel": "service",
                        "type": "application/json",
                        "title": "OGC API - Features"
                    }
                ]
            }
        ]
    
    if os.getenv("APP_DEBUG_MODE", "False") == "True":
        _LOGGER.warning("Disabling CORS")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add middleware to log request processing time
        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.perf_counter_ns()
            response = await call_next(request)
            process_time = time.perf_counter_ns() - start_time
            _LOGGER.debug(f"Request {request.method} '{request.url.path}' took {process_time / 1_000_000} ms")
            return response
        
    app.mount(FEATURES_ROUTE, features_api.init_api_server(), name="OGC API - Features")
    
    # Mount webserver, if it's not disabled
    if os.getenv("APP_DISABLE_WEB", "False") == "False":
        import server.web.start as webserver
        _LOGGER.info("Mounting webserver")
        
        flask_url = "/" + os.getenv("DASHBOARD_URL", "dashboard")
        app.mount(flask_url, WSGIMiddleware(webserver.create_app()))

    return app

def start_dev_api_server() -> None:
    print(os.getenv("API_SERVER_ROOT_PATH", ""))
    
    uvicorn.run(
        app="server.ogc_apis.start:init_main_api_server",
        host="0.0.0.0",
        port=int(os.getenv("HOST_PORT_API_SERVER", "8000")),
        proxy_headers=True,
        log_config=get_logger_config(True),
        log_level="debug",
        reload=True,
        reload_includes="./**/*.py",
        factory=True,
        loop="asyncio"
    )
    
def start_prod_api_server() -> uvicorn.Server:
    config = uvicorn.Config(
        app=init_main_api_server(),
        host="0.0.0.0",
        port=int(os.getenv("HOST_PORT_API_SERVER", "8000")),
        proxy_headers=True,
        log_config=get_logger_config(False),
        log_level="info",
        loop="uvloop"
    )
    return uvicorn.Server(config)