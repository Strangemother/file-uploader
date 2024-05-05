from django.db import models
from trim.models import fields


class EntryType(models.Model):
    """
    The _type_ of entry for a monitor record, such as "updated"
    """
    name = fields.chars()
    created, updated = fields.dt_cu_pair()
    def __str__(self):
        c = self.__class__.__name__
        return f'{c} "{self.name}"'


class MonitorRecord(models.Model):
    type = fields.fk(EntryType, nil=True)
    dt = fields.dt()
    created, updated = fields.dt_cu_pair()

    def __str__(self):
        c = self.__class__.__name__
        return f'{c} "{self.dt}"'


class MonitorEntry(models.Model):
    """We apply an entry to monitor. This is utilised for processing
    """
    # Path of the target.
    fullpath = fields.text()
    records = fields.m2m(MonitorRecord, nil=True)
    created, updated = fields.dt_cu_pair()

    def latest_record(self):
        return self.records.latest('created')

    def __str__(self):
        c = self.__class__.__name__
        return f'{c} "{self.fullpath}"'

