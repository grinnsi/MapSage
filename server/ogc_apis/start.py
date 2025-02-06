import uvicorn
import os

import server.ogc_apis.features.main as features_api
from server.config import get_logger_config

def start_dev_api_server() -> None:
    uvicorn.run(app="server.ogc_apis.features.main:init_api_server",
        port=int(os.getenv("APISERVER_PORT", "8000")),
        root_path=os.getenv("APISERVER_ROOT_PATH", ""),
        proxy_headers=True,
        log_config=get_logger_config(True),
        log_level="debug",
        reload=True,
        reload_includes="./**/*.py",
        factory=True
    )
    
def start_prod_api_server() -> uvicorn.Server:
    config = uvicorn.Config(
        app=features_api.init_api_server(),
        port=int(os.getenv("APISERVER_PORT", "8000")),
        root_path=os.getenv("APISERVER_ROOT_PATH", ""),
        proxy_headers=True,
        log_config=get_logger_config(False),
        log_level="warning"
    )
    return uvicorn.Server(config)