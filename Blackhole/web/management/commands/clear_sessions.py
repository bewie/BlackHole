# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
import os
import json
import datetime
from blackhole import settings

import redis

REDIS_SET_NAME = 'clients'

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        redis_server = redis.Redis(settings.redis_server)
        connections = redis_server.smembers(REDIS_SET_NAME)
        for key in connections:
            dict_connection = json.loads(key)
            pid = dict_connection['pid']
            is_running = True
            try:
                os.kill(pid, 0)
            except Exception as e:
                if e.errno == 3:
                    is_running = False
            if not is_running:
                print "Delete [%s] %s" % (datetime.datetime.now(), key)
                redis_server.srem(REDIS_SET_NAME, key)
