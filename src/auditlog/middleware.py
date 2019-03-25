import threading


class AuditlogMiddleware(object):
    """
    Middleware to couple the request's user to the logger in signal.
    """
    thread_local = threading.local()

    def process_request(self, request):
        """
        Gets the current user from the request and attaches it to the local thread.
        """

        # In case of proxy, set 'original' address
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            remote_addr = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
        else:
            remote_addr = request.META.get('REMOTE_ADDR')

        # Connect signal for automatic logging
        if hasattr(request, 'user') and self.is_authenticated(request.user):
            current_user = request.user
        else:
            current_user = None

        # Initialize thread local storage
        self.thread_local.auditlog = {
            'remote_addr': remote_addr,
            'current_user': current_user,
        }

    @classmethod
    def get_user(cls):
        if hasattr(cls.thread_local, 'auditlog'):
            return cls.thread_local.auditlog.get('current_user')

    @classmethod
    def get_remote_address(cls):
        if hasattr(cls.thread_local, 'auditlog'):
            return cls.thread_local.auditlog.get('remote_addr')

    def is_authenticated(self, user):
        """Return whether or not a User is authenticated.

        Function provides compatibility following deprecation of method call to
        `is_authenticated()` in Django 2.0.

        This is *only* required to support Django < v1.10 (i.e. v1.9 and earlier),
        as `is_authenticated` was introduced as a property in v1.10.s
        """
        if not hasattr(user, 'is_authenticated'):
            return False
        if callable(user.is_authenticated):
            # Will be callable if django.version < 2.0, but is only necessary in
            # v1.9 and earlier due to change introduced in v1.10 making
            # `is_authenticated` a property instead of a callable.
            return user.is_authenticated()
        else:
            return user.is_authenticated
