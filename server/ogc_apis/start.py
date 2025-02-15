import uvicorn
import os

import server.ogc_apis.features.main as features_api
from server.config import get_logger_config

def start_dev_api_server() -> None:
    uvicorn.run(
        app="server.ogc_apis.features.main:init_api_server",
        host="0.0.0.0",
        port=int(os.getenv("HOST_PORT_API_SERVER", "8000")),
        root_path=os.getenv("API_SERVER_ROOT_PATH", ""),
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
        app=features_api.init_api_server(),
        host="0.0.0.0",
        port=int(os.getenv("HOST_PORT_API_SERVER", "8000")),
        root_path=os.getenv("API_SERVER_ROOT_PATH", ""),
        proxy_headers=True,
        log_config=get_logger_config(False),
        log_level="info",
        loop="uvloop"
    )
    return uvicorn.Server(config)