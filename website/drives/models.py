from django.db import models
from trim.models import fields


class ContentNote(models.Model):
    fullpath = fields.text()
    text = fields.text()
    user = fields.user_fk(nil=True)
    created, updated = fields.dt_cu_pair()
