import logging
import sys
import os

level = logging.INFO
if os.environ.get('DEBUG_LOG'):
    level = logging.DEBUG

logger = logging.getLogger('fbsearch')
logger.setLevel(level)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.debug("Logging at level: %s", level)
