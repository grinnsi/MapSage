import os
import secrets

class WebserverConfig(object):
    def __init__(self) -> None:
        debug_mode = os.getenv("APP_DEBUG_MODE", "False") == "True"
        
        self.DEBUG = debug_mode           
        self.SECRET_KEY = "debug" if debug_mode else secrets.token_hex()
        self.PORT = int(os.getenv("HOST_PORT_WEB_SERVER", "4000"))