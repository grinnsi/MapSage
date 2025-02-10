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

def get_logger_config(debug_mode: bool) -> dict:
    return {
        'version': 1,
        'formatters': {
            'default': {
                '()': 'coloredlogs.ColoredFormatter',
                'format': '[%(asctime)s] %(levelname)-8s %(name)-30s in %(module)-20s %(message)s',
                'datefmt': '%H:%M:%S, %d-%m-%Y'
            }
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',  
            },
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
            },
            'asgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
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
                'handlers': ['default'],
                'propagate': False
            },
            "sqlalchemy.engine.Engine": {
                'level': "DEBUG" if debug_mode else "WARNING",
                "handlers": ["sqlalchemy"],
                'propagate': False
            },
            'uvicorn': {
                'level': "DEBUG" if debug_mode else "WARNING",
                'handlers': ['asgi'],
                'propagate': False
            },
            "uvicorn.error": {
                'level': "DEBUG" if debug_mode else "WARNING",
                'handlers': ['asgi'],
                'propagate': False
            },
            "uvicorn.access": {
                'level': "DEBUG" if debug_mode else "WARNING",
                'handlers': ['asgi'],
                'propagate': False
            },
            "uvicorn.asgi": {
                'level': "DEBUG" if debug_mode else "WARNING",
                'handlers': ['asgi'],
                'propagate': False
            }
        }
    }

# Method to set the logger configuration like colorscheme and formatting
def init_logger(logger_config: dict) -> None:
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
    dictConfig(logger_config)