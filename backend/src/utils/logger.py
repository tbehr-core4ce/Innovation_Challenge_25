import logging.config
import structlog

from settings import settings


def setup_logging(level: str):
    logging.basicConfig(
        format="%(message)s",
        level=level,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="%d %b %Y %H:%M:%S", key="time"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.EventRenamer(to="msg"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.dict_tracebacks,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    if not structlog.is_configured():
        setup_logging(settings.LOG_LEVEL)
    return structlog.get_logger(name)
