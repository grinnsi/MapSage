from argparse import ArgumentParser
from config import *

# Start program
if __name__ == '__main__':
    # Create cli-argument parser
    parser = ArgumentParser("ogc-api implementation", add_help=False)
    parser.add_argument("-h", "--help", help="Show this help message and exit", metavar='\b', dest="HELP")
    parser.add_argument("-d", "--debug", help="Enable debug mode", metavar='\b', dest="DEBUG")
    parser.add_argument("--disable-web", help="Disable the web interface", metavar='\b', dest="DISABLE_WEB")
    parser.add_argument("--disable-api", help="Disable the ogc api", metavar='\b', dest="DISABLE_API")

    # Create object for the arguments and parse the arguments into the object
    arguments = Arguments()
    parser.parse_args(namespace=arguments)
    
    # If the help message is printed, exit program
    if arguments.HELP:
        parser.print_help()
        exit(0)

    # Configure logger (colors, format, ...)
    Config.init_logger(arguments.DEBUG)