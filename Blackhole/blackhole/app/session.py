# -*- coding: utf-8 -*-
import logging
import signal
import os

from .client import DBClient, SecureShellClient


logger = logging.getLogger("blackhole.session")

class Session(object):
    def __init__(self, engine, host_connection):
        self._engine = engine
        self._host_connection = host_connection
        self._host_connection = host_connection
        self._user_identity = self._host_connection.get_connection_user(self._engine.user)
        logger.info(u"[login] user={0.current_user} as={1} to={2.name}({2.CONNECTION_TYPE}) session_uuid={0.session_uuid}".format(self._engine.setup, self._user_identity, self._host_connection.host))

    def connect(self, size):
        self._client.connect(self._host_connection.host.ip, self._host_connection.host.port, size)

    def start_session(self):
        raise NotImplementedError('Must Implement')

    def close_session(self):
        logger.info(u"[logout] user={0.current_user} as={1} to={2.name}({2.CONNECTION_TYPE}) session_uuid={0.session_uuid}".format(self._engine.setup, self._user_identity, self._host_connection.host))
        self._engine.session_ended_handler(self)

    def kill_session(self, signum, stack):
        logger.debug(u"Session Killed")
        self.close_session()
        os.kill(os.getpid(), signal.SIGKILL)


class SecureShellSession(Session):
    def __init__(self, engine, host_connection):
        super(SecureShellSession, self).__init__(engine, host_connection)
        self._client = SecureShellClient(self)
        logger.debug(u"SecureShellSession Created")

    def start_session(self):
        self._engine.session_started_handler(self)
        if self._host_connection.authentication_method == self._host_connection.AUTHENTICATION_METHOD_PRIVATE_KEY:
            logger.debug(u"Trying to validate using PK")
            pk = self._host_connection.get_private_key(self._user_identity)
            self.start_session_using_pk(pk)
        elif self._host_connection.authentication_method == self._host_connection.AUTHENTICATION_METHOD_PASSWORD:
            logger.debug(u"Trying to validate using Password")
            self.start_session_using_password(self._host_connection.password)
        else:
            logger.error(u"Unknown Authentication Method (%s)",  self._host_connection.authentication_method)
            raise Exception(u"Unknown Authentication Method (%s)" % self._host_connection.host_connection.authentication_method)

    def start_session_using_pk(self, private_key):
        self._client.start_session_using_pk(self._user_identity, private_key)

    def start_session_using_password(self, password):
        self._client.start_session_using_password(self._user_identity, password)


class DBSession(Session):
    def __init__(self, engine, host_connection):
        super(DBSession, self).__init__(engine, host_connection)
        self._client = DBClient(self)
        logger.debug(u"Database Session Created")

    def get_cmd(self):
        cmd = self._host_connection.get_client_command(self._engine.user)
        logger.debug(u"Running DB command {0}".format(cmd))
        return cmd

    def start_session(self):
        self._engine.session_started_handler(self)
        self._client.start_session()
        self.close_session()







