import os
import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from .config import *
from .web.start import start_web_server
from .database.db import Database

from dotenv import load_dotenv

# FIXME function gets called twice when starting
# Set environment variables from arguments, if they're not already set
# Order: OS -> .env file (only in debug mode) -> cli arguments
def set_env_variables(arguments: Arguments) -> None:
    # If debug enabled, load .env file
    if arguments.DEBUG_MODE:
        load_dotenv(verbose=True)
    
    # Get all attributes and values from arguments
    env_variables = {"APP_" + attr_name: arguments.__getattribute__(attr_name) for attr_name in dir(arguments) if not attr_name.startswith('__')}
    set_values = {}
    
    # Set env-variable for each attribute, if it doesn't exist
    for var, val in env_variables.items():
        if os.getenv(var) is None:
            os.environ[var] = str(val)
            set_values[var] = val
    
    # Log (debug level) all cli arguments, that have now been set as env-variable
    logger = logging.getLogger()
    logger.debug(msg="Setting cli environment variables: " + str(set_values))

# Read cli arguments and return them
def read_arguments() -> Arguments:
    # Create cli-argument parser
    parser = ArgumentParser(add_help=False, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-h", "--help", help="Show this help message and exit", action="store_true", dest="HELP")
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true", dest="DEBUG_MODE")
    parser.add_argument("--disable-web", help="Disable the web interface", action="store_true", dest="DISABLE_WEB")
    parser.add_argument("--disable-api", help="Disable the ogc api", action="store_true", dest="DISABLE_API")
    parser.add_argument("--db-dir", help="Absolute or relative path to the database directory", action="store", metavar="path", default=Arguments.DATABASE_DIR, dest="DATABASE_DIR")

    # Create object for the arguments and parse the arguments into the object
    arguments = Arguments()
    parser.parse_args(namespace=arguments)

    # Print help messae and exit program if help-flag set
    if arguments.HELP:
        parser.print_help()
        exit(0)
        
    return arguments
    
# Start program
if __name__ == '__main__':
    arguments = read_arguments()
    # Configure logger (colors, format, ...)
    init_logger(arguments.DEBUG_MODE)
    # Set environment variables
    set_env_variables(arguments)  
    # Init SQLite3 database
    Database.init_sqlite_db(arguments.DEBUG_MODE, False)
    
    # Start web (flask) server, if it's not disabled
    if not arguments.DISABLE_WEB:
        if arguments.DEBUG_MODE:
            # Start dev flask server
            start_web_server()
        else:
            # TODO Start production flask server
            pass
    
    # Start api (fastapi) server, if it's not disabled
    if not arguments.DISABLE_API:
        if arguments.DEBUG_MODE:
            # Start dev fastapi server
            pass
        else:
            # TODO Start production fastapi server
            pass