from django.db import models

from simple_history.models import HistoricalRecords


# Create your models here.
class BaseModel(models.Model):
    timestamp = models.DateTimeField('Fecha de creacion', auto_now=False, auto_now_add=True)
    historical = HistoricalRecords(user_model="users.User", inherit=True)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        """Meta definition for BaseModel."""
        abstract = True
        verbose_name = 'BaseModel'
        verbose_name_plural = 'BaseModels'