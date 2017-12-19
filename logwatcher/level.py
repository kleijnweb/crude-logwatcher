class LogLevel(object):
    DEBUG = "DEBUG"
    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    EMERGENCY = 'EMERGENCY'

    @staticmethod
    def as_dict():
        d = LogLevel.__dict__.items()
        return {
            key: value for key, value in d if isinstance(value, str) and '__' not in key
        }
