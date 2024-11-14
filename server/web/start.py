import os
from flask import Flask

from .config import WebserverConfig

# Init webserver
def create_app(config: WebserverConfig) -> Flask:     
    # Get absolute instance path (data-dir of module)
    instance_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    
    # Create app
    app = Flask("webserver", static_folder=os.path.join(instance_path, "static"), instance_relative_config=True, instance_path=instance_path)

    # Configure app (https://flask.palletsprojects.com/en/stable/tutorial/factory/)
    app.config.from_object(config)
    
    # Ensure instance/data folder exists
    try:
        os.makedirs(os.path.join(instance_path, "data"), exist_ok=True)
    except OSError:
        app.logger.critical("Error while creating Data-Directory", exc_info=OSError)
        raise
        
    @app.route('/interface', defaults={'path': ''})
    @app.route('/<path:path>')
    def get_interface(path):
        return app.send_static_file("index.html")
    
    return app

# TODO Dev Server, need different method for production
def start_web_server() -> None:
    config = WebserverConfig(True)
    app = create_app(config)
    app.run(port=config.PORT, debug=config.DEBUG)