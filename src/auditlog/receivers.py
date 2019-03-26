import json
import logging

from auditlog.diff import model_instance_diff
from auditlog.middleware import AuditlogMiddleware

logger = logging.getLogger("auditlogger")


def get_user_with_session():
    user = AuditlogMiddleware.get_user()
    if not user:
        user, session = 'An unauthenticated user', 'NO_SESSION'
    else:
        session = user.get_session_auth_hash()
    return user, session


def log_post_save(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is first saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    user, session = get_user_with_session()

    if created:
        changes = model_instance_diff(None, instance)
        msg = f"User '{user}' successfully created new object"
        logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})': '{json.dumps(changes)}'")
    else:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            changes = model_instance_diff(old, instance)

            msg = f"User '{user}' successfully updated object"
            logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})': '{json.dumps(changes)}'")


def log_pre_save(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is changed and saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """

    user, session = get_user_with_session()

    if instance.pk is None:
        changes = model_instance_diff(None, instance)
        msg = f"User '{user}({session})' attempting to create new object"
        logger.info(f"{msg} '{instance._meta.object_name}': '{json.dumps(changes)}'")
    else:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            changes = model_instance_diff(old, instance)

            msg = f"User '{user}({session})' attempting to change fields of"
            logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})': '{json.dumps(changes)}'")


def log_pre_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry just before a model instance is about to get deleted.
    """

    user, session = get_user_with_session()

    changes = model_instance_diff(instance, None)
    msg = f"User '{user}' attempting to delete object"
    logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})' with fields: '{json.dumps(changes)}'")


def log_post_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is deleted from the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        user, session = get_user_with_session()

        changes = model_instance_diff(instance, None)
        msg = f"User '{user}' successfully deleted"
        logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})' with fields: '{json.dumps(changes)}'")
