# Epilog extends the standard Python logging module.
#
# Epilog provides the following additional features:
# * New log level "NOTICE" as per Syslog standard.
# * Custom timestamp formatting (defaulting to ISO 8601 in UTC)
# * Support for JSON and text formatted logs
#
# Environment variables:
# * LOG_LEVEL: Set the logging level (default: INFO)
# * LOG_FORMAT: Set the logging format (json or text, default: text if stdout is a terminal, otherwise json)
# * LOG_TIMESTAMP_FORMAT: Set the timestamp format (default: ISO 8601 in UTC)
# * LOG_TIMESTAMP_FIELD: Set the timestamp field name in JSON logs (default: timestamp)
#
# Usage:
#   from epilog import EpiLog
#   logger = EpiLog(__name__)
#   logger.setLevel(logging.DEBUG) #  Probably redundant, use LOG_LEVEL 
#   logger.notice(msg)
#   logger.info(msg, extra={field: value, ...}

import sys
import os
import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger

class EpiLog(logging.Logger):
  # Set the timestamp format to ISO 8601 in UTC if not specified otherwise.
  def timeformat(datefmt=None) -> str:
    if datefmt:
      return datetime.now().astimezone().strftime(datefmt)
    else:
      return datetime.now(tz=timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


  # Custom text formatter class to override the default time formatting behavior. 
  class TextFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None) -> str:
      return EpiLog.timeformat(datefmt)


  # Custom json formatter class to override the default time formatting behavior. 
  class JsonFormatter(jsonlogger.JsonFormatter):
    def formatTime(self, record, datefmt=None) -> str:
      return EpiLog.timeformat(datefmt)

  class EpiFilter(logging.Filter):
    def filter(self, record):
      if hasattr(record, 'taskName') and not record.taskName:
        del record.taskName  # Remove taskName field if empty
      return True  # Allow all log records to pass through the filter

  # Initialize EpiLog
  def __init__(self, name, level=logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO')),
                 fmt='%(asctime)s %(levelname)-7s %(message)s',
                 rename_fields={ # Standardize field names for JSON output
                   'asctime': os.environ.get('LOG_TIMESTAMP_FIELD', 'timestamp'),
                   'levelname': 'level',
                   'message': 'msg'
                 }
               ):

    super().__init__(name, level)

    # Add NOTICE level as per Syslog standard
    setattr(logging, 'NOTICE', logging.INFO + 5)
    logging.addLevelName(logging.NOTICE, 'NOTICE')
    def notice(self, message, *args, **kws):
      if self.isEnabledFor(logging.NOTICE):
        self._log(logging.NOTICE, message, args, **kws) 
    logging.Logger.notice = notice

    self._handler = logging.StreamHandler(sys.stdout) # Add handler
    self._handler.addFilter(self.EpiFilter())  # Add the filter to the handler

    # Set up the logging handler based on LOG_FORMAT('json'/'text') env var or terminal
    self._format = os.environ.get('LOG_FORMAT', 'text' if sys.stdout.isatty() else 'json').lower()
    if self._format == 'json':
      self._handler.setFormatter(self.JsonFormatter(fmt=fmt, rename_fields=rename_fields, datefmt=os.environ.get('LOG_TIMESTAMP_FORMAT')))
    else:
      self._handler.setFormatter(self.TextFormatter(fmt, os.environ.get('LOG_TIMESTAMP_FORMAT', '%Y-%b-%d %H:%M:%S')))

    self.addHandler(self._handler)


  # Override setLevel to ensure both logger and handler levels are updated
  def setLevel(self, level):
    if level:
      super().setLevel(level)
      self._handler.setLevel(level)

# vim: set ts=2 sw=2 expandtab: 
