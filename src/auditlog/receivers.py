import json
import logging

from auditlog.diff import model_instance_diff
from auditlog.utils import get_default_log_message

logger = logging.getLogger("django.auditlogger")


def log_post_save(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is first saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    log_msg = get_default_log_message()

    if created:
        changes = model_instance_diff(None, instance)
        msg = f"{log_msg} successfully created new object"
        logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})': '{json.dumps(changes)}'")
    else:
        msg = f"{log_msg} successfully updated object"
        logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})'")


def log_pre_save(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is changed and saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """

    log_msg = get_default_log_message()

    if instance.pk is None:
        changes = model_instance_diff(None, instance)
        msg = f"{log_msg} attempting to create new object"
        logger.info(f"{msg} '{instance._meta.object_name}': '{json.dumps(changes)}'")
    else:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            changes = model_instance_diff(old, instance)

            msg = f"{log_msg} attempting to change fields of"
            logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})': '{json.dumps(changes)}'")


def log_pre_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry just before a model instance is about to get deleted.
    """

    log_msg = get_default_log_message()

    changes = model_instance_diff(instance, None)
    msg = f"{log_msg} attempting to delete object"
    logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})' with fields: '{json.dumps(changes)}'")


def log_post_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is deleted from the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        log_msg = get_default_log_message()

        changes = model_instance_diff(instance, None)
        msg = f"{log_msg} successfully deleted"
        logger.info(f"{msg} '{instance._meta.object_name}(id:{instance.pk})' with fields: '{json.dumps(changes)}'")
