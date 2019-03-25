from __future__ import unicode_literals

import json
import logging

from auditlog.diff import model_instance_diff
from auditlog.middleware import AuditlogMiddleware

logger = logging.getLogger("essarch.auditlog")


def get_user():
    auditlog = AuditlogMiddleware.thread_local.auditlog
    return auditlog.get('current_user')


def log_create(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is first saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if created:
        changes = model_instance_diff(None, instance)
        user = get_user()

        logger.info(f"{user}: in log_create with changes: '{json.dumps(changes)}'")


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
            user = get_user()

            # Log an entry only if there are changes
            if changes:
                logger.info(f"{user}: in log_update with changes: '{json.dumps(changes)}'")


def log_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is deleted from the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        changes = model_instance_diff(instance, None)
        user = get_user()
        logger.info(f"{user}: in log_delete with changes: '{json.dumps(changes)}'")
