import logging
import json

# General recommendation is to have a flat log structure, instead of embedded objects, to make it easier to query and analyze logs in log management systems.
RESERVED_ATTRS = {
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "module", "msecs",
    "message", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "thread", "threadName"
}

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "level": record.levelname,
            "message": record.getMessage(),       # handles % interpolation, and expands any args passed to logger.info("User %s logged in", username)
            "timestamp": self.formatTime(record),
            "logger": record.name,                # useful when you have multiple loggers, optional in this case
        }

        # Capture exception tracebacks - the exception key is created that defines the string representation of the exception, and any stack trace information if available. This is crucial for debugging errors.
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Capture any extra={} fields passed to the logger - this aims to please the top requirement of having a flat log structure.
        extras = {k: v for k, v in record.__dict__.items() if k not in RESERVED_ATTRS}
        log_obj.update(extras)

        return json.dumps(log_obj)


logger = logging.getLogger()
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
