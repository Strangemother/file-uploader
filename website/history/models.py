from django.db import models
from trim.models import fields


class PathAccess(models.Model):
    """A Historical path access.
    """
    reaccess_count = fields.int(0)
    fullpath = fields.text()
    created = fields.dt_created()

    @classmethod
    def add(cls, fullpath, dbname='history'):
        prev = cls.objects.using(dbname).latest('created')
        if prev.fullpath == fullpath:
            # We can skip - it's a copy.
            prev.reaccess_count += 1
            prev.save()
            return prev.id
        v = cls.objects.using(dbname).create(fullpath=fullpath)
        return v.id
