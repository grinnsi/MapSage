import os
import secrets

class WebserverConfig(object):
    def __init__(self, debug_mode: bool) -> None:
        if debug_mode:
           self.DEBUG = True
                       
           from dotenv import load_dotenv
           load_dotenv(verbose=True)
           
        self.SECRET_KEY = "debug" if debug_mode else secrets.token_hex()
        self.PORT = os.getenv("WEBSERVER_PORT", 4000)