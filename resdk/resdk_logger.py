"""
*********************
Logging configuration
*********************

Module contents:

#. Parent logger for all modules in resdk library
#. Handlers STDOUT_HANDLER and FILE_HANDLER ("turned off" by default)
#. Handler configuration functions
#. Override sys.excepthook to log all uncaught exceptions


1. Parent logger for all modules in resdk library
=================================================
Loggers in resdk are named by their module name. This is achieved by::

    logger = logging.getLogger(__name__)

This makes it easy to locate the souce of a log message.


2. Handlers STDOUT_HANDLER and FILE_HANDLER ("turned off" by default)
=====================================================================

Two basic handlers are created but not yet added to ROOT_LOGGER, which means
they cannot do anything. Only whern user calls ``start_logging()``
or other functions to configure handlers, these handlers are activated.


3. Handler configuration functions
==========================================
As a good logging practice, library itself should never register handlers by
default. The reason is that if the library is included in some application,
developers of that application will probably want to register loggers by
themself. Therefore, if a user wishes to register the pre-defined handlers
(which are not activated by default) he/she should add a line of code::

    import resdk
    resdk.start_logging()

    normal code...

.. Useful links:
.. http://pieces.openpolitics.com/2012/04/python-logging-best-practices/
.. http://pythonsweetness.tumblr.com/post/67394619015/use-of-logging-package-from-within-a-library


4. Override sys.excepthook to log all uncaught exceptions
=========================================================

All python exceptions are handled by function, stored in ``sys.excepthook.``
By rewriting the default implementation, we can modify it for our puruses - to
log all uncaught exceptions.

Note#1: modified behaviour (logging of all uncaught exceptions) applies only
when runing in non-interactive mode.

Note#2:
Any exception can be caught/uncaought and it can happen in
interactive/non-interactive mode. This makes 4 different scenarios. The
sys.excepthook modification takes care of uncaught exceptions in
non-interactive mode. In interactive mode, user is notified directly if
exception is raised. If exception is caught and not reraised, it should be
logged somehow, since it can provide valuable information for developer when
debugging. Therefore, we should use the following convention for logging in
resdk: "Exceptions are explicitly logged only when they are caught and
not re-raised."

.. Useful links:
.. https://docs.python.org/2/library/sys.html#sys.excepthook
.. http://stackoverflow.com/questions/5451746/sys-excepthook-doesnt-work-in-imported-modules?rq=1
.. http://bugs.python.org/issue11705
"""
import os
import sys
import logging

from six import string_types

LEVEL_MAP = {"DEBUG": logging.DEBUG,
             "INFO": logging.INFO,
             "WARNING": logging.WARNING,
             "ERROR": logging.ERROR,
             "EXCEPTION": logging.ERROR,
             "CRITICAL": logging.CRITICAL}

#######################################################################
LOGGER_NAME = __name__.split('.')[0]

# Create root logger:
ROOT_LOGGER = logging.getLogger(LOGGER_NAME)
# Set to lowest threshold possible, since specific handlers can
# increase threshold level, if neccessary:
ROOT_LOGGER.setLevel(logging.DEBUG)  # lowest possible value

# Create "do-nothing" handler. Why? If both (file and stdout handlers) are turned off,
# having NullHandler prevents message: "No handlers could be found for logger XXXX".
ROOT_LOGGER.addHandler(logging.NullHandler())

#######################################################################
# Default settings for stdout handler:
STDOUT_LOG_LEVEL = logging.INFO
STDOUT_LOG_ON = True

# Default settings for file handler:
FILE_LOG_LEVEL = logging.WARNING
FILE_LOG_ON = False
FILE_LOG_PATH = os.path.join(os.path.dirname(__file__), 'logfile.txt')


# Create stdout handler and make initial configuration:
STDOUT_HANDLER = logging.StreamHandler()
FORMATTER1 = logging.Formatter(fmt='%(message)s')
STDOUT_HANDLER.setFormatter(FORMATTER1)

# Create file handler and make initial configuration:
FILE_HANDLER = logging.FileHandler(FILE_LOG_PATH)
FORMATTER2 = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
FILE_HANDLER.setFormatter(FORMATTER2)

#######################################################################


def _configure_handler(handler, is_on=None, level=None):
    """
    Helper function for configuring handlers.

    If parameter is not provided, it's value will not change.

    :param is_on: If True, log to standard output
    :type is_on: bool
    :param level: logging threshold level
    :type level: int in [0-50]

    :rtype: None
    """
    if is_on is not None:
        if isinstance(is_on, bool):
            if is_on:
                ROOT_LOGGER.addHandler(handler)
            else:
                ROOT_LOGGER.removeHandler(handler)
        else:
            raise ValueError("Wrong type of 'is_on' parameter: only True/False/None posssible.")

    if level is not None:
        if isinstance(level, string_types) and level.upper() in LEVEL_MAP.keys():
            handler.setLevel(LEVEL_MAP[level.upper()])
        elif isinstance(level, int) and level >= 0 and level <= 50:
            handler.setLevel(level)
        else:
            raise ValueError("Wrong value of 'level' parameter.")


def log_to_stdout(is_on=None, level=None):
    """
    Configure logging to stdout.

    :param is_on: If True, log to standard output
    :type is_on: bool
    :param level: logging threshold level - integer in [0-50]
    :type level: int

    :rtype: None
    """
    _configure_handler(STDOUT_HANDLER, is_on=is_on, level=level)


def log_to_file(is_on=None, level=None, path=None):
    """
    Configure logging to file.

    :param is_on: If True, log to file
    :type is_on: bool
    :param level: logging threshold level - integer in [0-50]
    :type level: int

    :rtype: None
    """
    if path is not None:
        global FILE_HANDLER  # pylint: disable=global-statement
        old_level = FILE_HANDLER.level
        # rewrite the FILE_HANDLER instance and configure as before:
        ROOT_LOGGER.removeHandler(FILE_HANDLER)
        FILE_HANDLER = logging.FileHandler(path)
        FILE_HANDLER.setLevel(old_level)
        FILE_HANDLER.setFormatter(FORMATTER2)

    _configure_handler(FILE_HANDLER, is_on=is_on, level=level)


def start_logging(logging_level=logging.INFO):
    """
    Start logging resdk with the default configuration

    :param logging_level: logging threshold level - integer in [0-50]
    :type logging_level: int
    :rtype: None

    Logging levels:

    * logging.DEBUG(10)
    * logging.INFO(20)
    * logging.WARNING(30)
    * logging.ERROR(40)
    * logging.CRITICAL(50)
    """
    log_to_stdout(is_on=STDOUT_LOG_ON, level=logging_level or STDOUT_LOG_LEVEL)
    log_to_file(is_on=FILE_LOG_ON, level=logging_level or FILE_LOG_LEVEL)


# #####################################################################

def _log_all_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """
    Log all uncaught exceptions in non-interactive mode.

    All python exceptions are handled by function, stored in
    ``sys.excepthook.`` By rewriting the default implementation, we
    can modify handling of all uncaught exceptions.

    Warning: modified behaviour (logging of all uncaught exceptions)
    applies only when runing in non-interactive mode.
    """
    # ignore KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    ROOT_LOGGER.error("", exc_info=(exc_type, exc_value, exc_traceback))

# Rewrite the default implementation os sys.excepthook to log all
# uncaught exceptions:
sys.excepthook = _log_all_uncaught_exceptions
