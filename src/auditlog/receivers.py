import json
import logging

from auditlog.diff import model_instance_diff
from auditlog.middleware import AuditlogMiddleware

logger = logging.getLogger("essarch.auditlog")


def log_create(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is first saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if created:
        changes = model_instance_diff(None, instance)
        user = AuditlogMiddleware.get_user()
        if not user:
            user = 'An unauthenticated user'

        msg = f"User '{user}' created new object"
        logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})': '{json.dumps(changes)}'")


def log_update(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is changed and saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            new = instance
            changes = model_instance_diff(old, new)
            user = AuditlogMiddleware.get_user()
            if not user:
                user = 'An unauthenticated user'

            # Log an entry only if there are changes
            if changes:
                msg = f"User '{user}' changed fields of"
                logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})': '{json.dumps(changes)}'")


def log_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is deleted from the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        changes = model_instance_diff(instance, None)
        user = AuditlogMiddleware.get_user()
        if not user:
            user = 'An unauthenticated user'
        msg = f"User '{user}' deleted"
        logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})' with fields: '{json.dumps(changes)}'")
