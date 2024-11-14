from argparse import ArgumentParser
from config import *
from web.start import start_web_server

# Read cli arguments and return them
def read_arguments() -> Arguments:
    # Create cli-argument parser
    parser = ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", help="Show this help message and exit", action="store_true", dest="HELP")
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true", dest="DEBUG")
    parser.add_argument("--disable-web", help="Disable the web interface", action="store_true", dest="DISABLE_WEB")
    parser.add_argument("--disable-api", help="Disable the ogc api", action="store_true", dest="DISABLE_API")

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
    Config.init_logger(arguments.DEBUG)
    
    # Start web (flask) server, if it's not disabled
    if not arguments.DISABLE_WEB:
        if arguments.DEBUG:
            # Start dev flask server
            start_web_server()
        else:
            # TODO Start production flask server
            pass
    
    # Start api (fastapi) server, if it's not disabled
    if not arguments.DISABLE_API:
        if arguments.DEBUG:
            # Start dev fastapi server
            pass
        else:
            # TODO Start production fastapi server
            pass