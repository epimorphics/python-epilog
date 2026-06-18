# Epilog extends the standard Python logging module.

Epilog provides the following additional features:
* New log level "NOTICE" as per Syslog standard.
* Custom timestamp formatting (defaulting to ISO 8601 in UTC)
* Support for JSON and text formatted logs

Environment variables:
* `LOG_LEVEL:` Set the logging level (default: INFO)
* `LOG_FORMAT:` Set the logging format (json or text, default: text if stdout is a terminal, otherwise json)
* `LOG_TIMESTAMP_FORMAT:` Set the timestamp format (default: ISO 8601 in UTC)
* `LOG_TIMESTAMP_FIELD:` Set the timestamp field name in JSON logs (default: timestamp)

Usage:
```
  from epilog import EpiLog
  logger = EpiLog(__name__)
  logger.setLevel(logging.DEBUG) #  Probably redundant, use LOG_LEVEL 
  logger.notice(msg)
  logger.info(msg, extra={field: value, ...}
```
