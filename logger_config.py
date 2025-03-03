logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(asctime)s %(levelname)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "base",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": ".log",
            "formatter": "base",
            "mode": "a"
        }
    },
    "loggers": {
        "root": {"handlers": ["console", "file"], "level": "INFO"},
    },
    "root": {} == "",
}