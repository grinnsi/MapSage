import os
from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from .settings.routes import create_data_endpoints

from .config import WebserverConfig

# Init webserver
def create_app(config: WebserverConfig) -> Flask:     
    # Get absolute instance path (data-dir of module)
    instance_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    
    # Create app
    app = Flask(__name__, static_folder=os.path.join(instance_path, "static"), instance_relative_config=True, instance_path=instance_path)
    # TODO Set number of proxies, depending on env-variable or user input
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # Configure app (https://flask.palletsprojects.com/en/stable/tutorial/factory/)
    app.config.from_object(config)
    
    # Ensure instance/data folder exists
    try:
        os.makedirs(os.path.join(instance_path, "data"), exist_ok=True)
    except OSError:
        app.logger.critical("Error while creating Data-Directory", exc_info=OSError)
        raise

    # Catch /dashboard/... requests; Send index.html, and nessecary files
    @app.route('/dashboard/')
    @app.route('/dashboard/<path:path>')
    def get_dashboard(path="index.html"):
        # If url path is not a file (like options, namesapces) then add index.html to path
        if path.count('.') == 0:
            path += f"/index.html"

        return send_from_directory(app.static_folder, path)
    
    app.register_blueprint(create_data_endpoints())
    
    return app

# TODO Dev Server, need different method for production
def start_web_server() -> None:
    config = WebserverConfig(True)
    app = create_app(config)
    app.run(port=config.PORT, debug=config.DEBUG)