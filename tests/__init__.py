import logging

_log = logging.getLogger(__name__)

def _setupLog():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    _log.addHandler(handler)
    _log.setLevel(logging.DEBUG)

_setupLog()
