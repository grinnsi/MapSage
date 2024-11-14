# Class as namespace for arguments (for autocomplete and more)
class Arguments(object):
    HELP = False
    DEBUG = False
    DISABLE_WEB = False
    DISABLE_API = False

# Class to group configuration methods/variables
class Config(object):
    @staticmethod
    def init_logger(debug_mode: bool):
        pass