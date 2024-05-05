from django.db import models
from trim.models import fields


class PathAccess(models.Model):
    """A Historical path access.
    """
    fullpath = fields.text()
    created = fields.dt_created()

    @classmethod
    def add(cls, fullpath, dbname='history'):
        v = cls.objects.using(dbname).create(fullpath=fullpath)
        return v.id
