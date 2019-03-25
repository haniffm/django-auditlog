from __future__ import unicode_literals

import threading
import time
import logging

from auditlog.util import is_authenticated

threadlocal = threading.local()
logger = logging.getLogger('essarch.auditlog')


class AuditlogMiddleware(object):
    """
    Middleware to couple the request's user to log items. This is accomplished by currying the signal receiver with the
    user from the request (or None if the user is not authenticated).
    """
    thread_local = threading.local()

    def process_request(self, request):
        """
        Gets the current user from the request and prepares and connects a signal receiver with the user already
        attached to it.
        """
        # Initialize thread local storage
        threadlocal.auditlog = {
            'signal_duid': (self.__class__, time.time()),
            'remote_addr': request.META.get('REMOTE_ADDR'),
        }

        # In case of proxy, set 'original' address
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            threadlocal.auditlog['remote_addr'] = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]

        # Connect signal for automatic logging
        if hasattr(request, 'user') and is_authenticated(request.user):
            threadlocal.auditlog['current_user'] = request.user
        else:
            logger.info("request has no user attr!")

        AuditlogMiddleware.thread_local = threadlocal
