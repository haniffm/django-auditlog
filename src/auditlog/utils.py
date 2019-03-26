
from auditlog.middleware import AuditlogMiddleware


def get_user_with_session():
    user = AuditlogMiddleware.get_user()
    if not user:
        user, session = 'An unauthenticated user', 'NO_SESSION'
    else:
        session = user.get_session_auth_hash()
    return user, session


def get_default_log_message():
    user, session = get_user_with_session()
    remote_addr = AuditlogMiddleware.get_remote_address()
    return f"{remote_addr} user '{user}' {session}"
