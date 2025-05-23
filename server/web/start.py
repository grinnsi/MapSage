import logging
import os
from flask import Flask, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from server.web.collections.collection_routes import create_collections_endpoints
from server.web.datasets.routes import create_datasets_endpoints
from server.web.settings.routes import create_settings_endpoints
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
        os.makedirs(os.path.join(instance_path, "instance"), exist_ok=True)
    except OSError:
        app.logger.critical("Error while creating Instance-Directory", exc_info=OSError)
        raise
    
    # Add logging middleware if app in debug mode
    if config.DEBUG:
        @app.before_request
        def log_request_info():
            app.logger.debug(f"Flask Request: {request.url} {request.method} {request.get_json() if request.data else ''}")

    # Catch /dashboard/... requests; Send index.html, and necessary files
    @app.route('/' if os.getenv("APP_DISABLE_API", "False") == "False" else '/dashboard/')
    @app.route('/<path:path>' if os.getenv("APP_DISABLE_API", "False") == "False" else '/dashboard/<path:path>')
    def get_dashboard(path="index.html"):       
        # If url path is not a file (like options, namespaces) then add index.html to path
        if path.count('.') == 0:
            path += f"/index.html"

        return send_from_directory(app.static_folder, path)
    
    main_data_endpoint = "/data"
    
    app.register_blueprint(create_settings_endpoints(main_data_endpoint))
    app.register_blueprint(create_datasets_endpoints(main_data_endpoint))
    app.register_blueprint(create_collections_endpoints(main_data_endpoint))
    
    return app

def start_dev_web_server() -> None:
    config = WebserverConfig()
    app = create_app(config)
    
    # Init SQLite database
    with app.app_context():
        Database.init_sqlite_db(False)
    
    logging.getLogger().info("Starting development webserver")
    app.run(port=config.PORT, debug=config.DEBUG)