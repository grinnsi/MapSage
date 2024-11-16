from os.path import abspath
from logging.config import dictConfig
import coloredlogs

# Class as namespace for arguments (for autocomplete and more)
class Arguments(object):
    HELP = False
    DEBUG_MODE = False
    DISABLE_WEB = False
    DISABLE_API = False
    DATABASE_DIR = abspath("./data")

# Class to group configuration methods/variables
def init_logger(debug_mode: bool):
    coloredlogs.DEFAULT_LEVEL_STYLES = dict(
        spam=dict(color=22, faint=True),
        debug=dict(color=28),
        verbose=dict(color=34),
        info=dict(),
        notice=dict(color=220),
        warning=dict(color=202),
        success=dict(color=118, bold=True),
        error=dict(color=124, bold=True),
        critical=dict(color=196, background='white', inverse=True, bright=True),
    )
    coloredlogs.DEFAULT_FIELD_STYLES = dict(
        asctime=dict(color='cyan'),
        hostname=dict(color='magenta'),
        levelname=dict(color=13, bold=True),
        name=dict(color='blue'),
        programname=dict(color='cyan'),
        username=dict(color='yellow'),
    )
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                '()': 'coloredlogs.ColoredFormatter',
                'format': '[%(asctime)s] %(levelname)-8s in %(module)-20s %(message)s',
                'datefmt': '%H:%M:%S, %d-%m-%Y'
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
            },
            "sqlalchemy": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            '': {
                'level': 'DEBUG' if debug_mode else "WARNING",
                'handlers': ['wsgi']
            },
            "sqlalchemy.engine.Engine": {
                'level': "DEBUG" if debug_mode else "WARNING",
                "handlers": ["sqlalchemy"],
                'propagate': False
            },
        }
    })