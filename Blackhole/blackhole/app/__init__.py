# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import SysLogHandler
from blackhole import settings

logger = logging.getLogger("blackhole")
logger.setLevel(settings.log_level)
if settings.log_level == logging.DEBUG:
    if os.path.isfile("/tmp/blackhole.log"):
        if os.access("/tmp/blackhole.log", os.W_OK):
            log_handler = logging.FileHandler("/tmp/blackhole.log")
        else:
            log_handler = SysLogHandler(address='/dev/log')
    else:
        log_handler = logging.FileHandler("/tmp/blackhole.log")
else:
    log_handler = SysLogHandler(address='/dev/log')
log_handler.setFormatter(logging.Formatter('%(asctime)s - BlackHole - %(levelname)s: %(message)s'))
logger.addHandler(log_handler)
