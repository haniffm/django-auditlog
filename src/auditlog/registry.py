from __future__ import unicode_literals

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models import Model


class AuditlogModelRegistry(object):
    """
    A registry that keeps track of the models that use Auditlog to track changes.
    """
    def __init__(self, custom=None):
        from auditlog.receivers import log_pre_save, log_post_save, log_pre_delete, log_post_delete

        self._registry = {}
        self._signals = {
            pre_save: log_pre_save,
            post_save: log_post_save,
            pre_delete: log_pre_delete,
            post_delete: log_post_delete
        }

        if custom:
            self._signals.update(custom)

    def register(self, model=None, m2m=False, include_fields=[], exclude_fields=[], mask_value_fields=[]):
        """
        Register a model with auditlog. Auditlog will then track mutations on this model's instances.

        :param model: The model to register.
        :type model: Model
        :param m2m: If many to many models should be checked as well.
        :type m2m: bool
        :param include_fields: The fields to include. Implicitly excludes all other fields.
        :type include_fields: list
        :param exclude_fields: The fields to exclude. Overrides the fields to include.
        :type exclude_fields: list
        :param mask_value_fields: The fields to mask the values of.
        :type mask_value_fields: list
        """
        def registrar(cls):
            if m2m:
                raise NotImplementedError("We do not have support for m2m fields yet. Set m2m param to false.")

            """Register models for a given class."""
            if not issubclass(cls, Model):
                raise TypeError("Supplied model is not a valid model.")

            self._registry[cls] = {
                'include_fields': include_fields,
                'exclude_fields': exclude_fields,
                'mask_value_fields': mask_value_fields,
                'm2m': m2m,
            }
            self._connect_signals(cls)

            # We need to return the class, as the decorator is basically
            # syntactic sugar for:
            # MyClass = auditlog.register(MyClass)
            return cls

        if model is None:
            # If we're being used as a decorator, return a callable with the
            # wrapper.
            return lambda cls: registrar(cls)
        else:
            # Otherwise, just register the model.
            registrar(model)

    def contains(self, model):
        """
        Check if a model is registered with auditlog.

        :param model: The model to check.
        :type model: Model
        :return: Whether the model has been registered.
        :rtype: bool
        """
        return model in self._registry

    def unregister(self, model):
        """
        Unregister a model with auditlog. This will not affect the database.

        :param model: The model to unregister.
        :type model: Model
        """
        try:
            del self._registry[model]
        except KeyError:
            pass
        else:
            self._disconnect_signals(model)

    def _connect_signals(self, model):
        """
        Connect signals for the model.
        """
        for signal in self._signals:
            receiver = self._signals[signal]
            signal.connect(receiver, sender=model, dispatch_uid=self._dispatch_uid(signal, model))

    def _disconnect_signals(self, model):
        """
        Disconnect signals for the model.
        """
        for signal, receiver in self._signals.items():
            signal.disconnect(sender=model, dispatch_uid=self._dispatch_uid(signal, model))

    def _dispatch_uid(self, signal, model):
        """
        Generate a dispatch_uid.
        """
        return self.__class__, model, signal

    def get_model_fields(self, model):
        return {
            'include_fields': self._registry[model]['include_fields'],
            'exclude_fields': self._registry[model]['exclude_fields'],
            'mask_value_fields': self._registry[model]['mask_value_fields'],
        }


auditlog = AuditlogModelRegistry()
