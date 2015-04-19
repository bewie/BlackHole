# -*- coding: utf-8 -*-
import json
import logging
import os
import pytz
import uuid
from datetime import datetime
import socket
import getpass
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blackhole.settings")
import redis
import paramiko
from django.core import exceptions
from django import db
from blackhole import settings
from blackhole.app.watcher import IOHandler
from web import models
from .gui import Window
from .session import SecureShellSession, DBSession

logger = logging.getLogger("blackhole.engine")

REDIS_SET_NAME = "clients"

class Setup(object):
    def __init__(self, django_settings):
        self.redis_server = django_settings.redis_server
        self.debug = django_settings.DEBUG
        self.log_path = django_settings.log_path
        self.timezone = django_settings.TIME_ZONE
        remote_host_information = os.environ.get('SSH_CLIENT', '0.0.0.0 0')
        self.source_ip = remote_host_information.split()[0]
        self.source_port = remote_host_information.split()[1]
        self.session_uuid = uuid.uuid1()
        self.current_user = getpass.getuser()
        self.pid = os.getpid()
        self.ppid = os.getppid()


class Blackhole(object):
    def __init__(self):
        logger.debug(u"BlackHole App Started")
        self.setup()
        self.redis_session_data = None
        self.build_gui()
        self.iohanlder = IOHandler()

    def setup(self):
        self.setup = Setup(settings)
        try:
            self.refresh_user()
        except exceptions.ObjectDoesNotExist:
            logger.error(u"User %s doesn't exist" % self.setup.current_user)
            self.user = None
        logger.debug(u"Setup Complete")

    def refresh_user(self):
        self.user = models.AppUser.objects.get(username=self.setup.current_user)

    def build_gui(self):
        self.gui = Window(self)
        if not self.user:
            self.gui.show_notification(u"Unknown user: %s" % self.setup.current_user)
        db.close_connection()

    def __str__(self):
        return u"[auth] user={0.current_user} from={0.source_ip}:{0.source_port} pid={0.pid} session_uuid={0.session_uuid}".format(self.setup)

    def run(self):
        logger.info(self)
        self.gui.start_ui()

    def get_environments(self):
        if self.user:
            return self.user.profile.get_environments()
        else:
            return []

    def get_user_full_name(self):
        return self.user.get_full_name() if self.user else u"-"

    def validate_user(self, host):
        self.refresh_user()
        if not self.user.enabled:
            message = u"The user %s is disabled" % self.user.get_full_name()
            logger.debug(message)
            raise Exception(message)
        else:
            if self.user.time_range_enabled:
                now = datetime.now().time().replace(second=0)
                allow_connection = False
                if self.user.time_range_enabled_since < now:
                    allow_connection = True
                    if now < self.user.time_range_enabled_to:
                        allow_connection = True
                    else:
                        allow_connection = False
                else:
                    allow_connection = False
                if not allow_connection:
                    raise Exception(u"Connections are allowed from %s to %s" % (self.user.time_range_enabled_since,  self.user.time_range_enabled_to))
            environments = self.user.allowed_environments.all()
            if environments:
                if host.environment not in environments:
                    raise Exception(u"Connection to the environment %s is not allowed" % host.environment)

    def quit(self):
        logger.debug(u"Quit Application")
        self.gui.stop_ui()

    def start_connection(self, host_widget):
        db.close_connection()
        if not os.path.isdir(self.setup.log_path):
            logger.error(u"Logs Path not found")
            raise Exception(u"Logs Path not found")
        self.validate_user(host_widget.host_connection.host)
        session = self.create_session(host_widget)
        size = self.gui.loop.screen.get_cols_rows()
        self.gui.pause_screen()
        try:
            session.connect(size)
        except socket.timeout as e:
            logger.error(u"Connection Failed <{0}> [{1}]".format(e.message, host_widget.host_connection.host.name))
            raise Exception(u"Connection Failed <{0}>".format(e.message))
        except socket.error as e:
            logger.error(u"Connection Failed <{0}> [{1}]".format(e, host_widget.host_connection.host.name))
            raise Exception(u"Connection Failed <{0}>".format(e))
        except Exception as e:
            logger.error(u"Connection Failed <{0}> [{1}]".format(e, host_widget.host_connection.host.name))
            raise Exception(u"Connection Failed <{0}>".format(e))
        self.iohanlder.set_log_filename(session.session_log.log_file)
        self.iohanlder.capture()
        try:
            session.start_session()
        except paramiko.AuthenticationException as e:
            msg = u"Authentication Failed <{0}>".format(e)
            logger.error(msg)
            raise Exception(msg)
        except Exception as e:
            msg = u"ERROR <{0}>".format(e)
            #logger.error(msg)
            raise Exception(msg)
        finally:
            self.iohanlder.restore()

    def create_session(self, host_widget):
        logger.debug(u"Creating Session")
        if host_widget.host_connection.host.CONNECTION_TYPE == models.CONNECTION_TYPE_SSH:
            try:
                session = SecureShellSession(self, host_widget.host_connection)
            except:
                raise
        elif host_widget.host_connection.host.CONNECTION_TYPE == models.CONNECTION_TYPE_DB:
            try:
                session = DBSession(self, host_widget.host_connection)
            except:
                raise
        else:
            logger.error(u'Unknown Connection Type')
            raise Exception(u'Unknown Connection Type')
        session.session_log = models.SessionLog()
        session.session_log.session_type = host_widget.host_connection.host.CONNECTION_TYPE
        session.session_log.user = self.user
        session.session_log.login_date = datetime.now(pytz.timezone(self.setup.timezone))
        session.session_log.session_id = self.setup.session_uuid
        session.session_log.source_ip = self.setup.source_ip
        session.session_log.host = host_widget.host_connection.host.name
        session.session_log.user_identity = host_widget.host_connection.get_connection_user(self.user)
        session.session_log.log_file = session.session_log.get_log_filename(os.path.join(self.setup.log_path, self.user.username))
        logger.debug("session log: %s", session.session_log.log_file)
        session.session_log.save()
        return session

    def session_started_handler(self, session):
        logger.debug("Start session handler")
        json_data = {'session_id': str(self.setup.session_uuid),
                     'host': session.session_log.host,
                     'session_type': session.session_log.session_type,
                     'real_user': self.setup.current_user,
                     'session_user': session.session_log.user_identity,
                     'source_ip': self.setup.source_ip,
                     'login_date': str(session.session_log.login_date),
                     'pid': self.setup.pid,
                     'id': session.session_log.id}
        self.redis_session_data = json.dumps(json_data)
        self.add_to_redis()

    def session_ended_handler(self, session):
        logger.debug("Stop session handler")
        db.close_connection()
        session.session_log.logout_date = datetime.now(pytz.timezone(self.setup.timezone))
        session.session_log.save_duration()
        session.session_log.save()
        self.remove_from_redis()

    def add_to_redis(self):
        try:
            redis_server = redis.Redis(self.setup.redis_server)
            redis_server.sadd(REDIS_SET_NAME, self.redis_session_data)
            logger.debug("Session added to redis")
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis Connection <{0}>".format(e))
            raise
        except Exception as e:
            logger.error("Redis Unknown <{0}>".format(e))
            raise

    def remove_from_redis(self):
        try:
            redis_server = redis.Redis(self.setup.redis_server)
            redis_server.srem(REDIS_SET_NAME, self.redis_session_data)
            self.redis_session_data = None
            logger.debug("Session removed from redis")
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis Connection <{0}>".format(e))
            raise
        except Exception as e:
            logger.error("Redis Unknown <{0}>".format(e))
            raise
