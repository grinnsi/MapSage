import logging
import os
from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from server.web.settings.routes import create_data_endpoints
from server.web.config import WebserverConfig
from server.database.db import Database

# Init webserver
def create_app(config: WebserverConfig = None) -> Flask:     
    # Get absolute instance path (data-dir of module)
    instance_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    
    # Create app
    app = Flask("server.web", static_folder=os.path.join(instance_path, "static"), instance_relative_config=True, instance_path=instance_path)
    # TODO Set number of proxies, depending on env-variable or user input
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # Configure app (https://flask.palletsprojects.com/en/stable/tutorial/factory/)
    if config is None:
        config = WebserverConfig()
    
    app.config.from_object(config)
    
    # Ensure instance/data folder exists
    try:
        os.makedirs(os.path.join(instance_path, "data"), exist_ok=True)
    except OSError:
        app.logger.critical("Error while creating Data-Directory", exc_info=OSError)
        raise

    # Catch /dashboard/... requests; Send index.html, and necessary files
    @app.route('/' if os.getenv("APP_DISABLE_API", "False") == "False" else '/dashboard/')
    @app.route('/<path:path>' if os.getenv("APP_DISABLE_API", "False") == "False" else '/dashboard/<path:path>')
    def get_dashboard(path="index.html"):       
        # If url path is not a file (like options, namespaces) then add index.html to path
        if path.count('.') == 0:
            path += f"/index.html"

        return send_from_directory(app.static_folder, path)
    
    app.register_blueprint(create_data_endpoints())
    
    return app

def start_dev_web_server() -> None:
    config = WebserverConfig()
    app = create_app(config)
    
    # Init SQLite database
    with app.app_context():
        Database.init_sqlite_db(False)
    
    logging.getLogger().info("Starting development webserver")
    app.run(port=config.PORT, debug=config.DEBUG)