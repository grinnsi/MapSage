import os
import secrets

class WebserverConfig(object):
    def __init__(self, debug_mode: bool) -> None:
        self.DEBUG = debug_mode           
        self.SECRET_KEY = "debug" if debug_mode else secrets.token_hex()
        self.PORT = os.getenv("WEBSERVER_PORT", 4000)