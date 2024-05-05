from django.db import models
from trim.models import fields


class ContentLink(models.Model):
    fullpath = fields.text()
    created, updated = fields.dt_cu_pair()


class Box(models.Model):
    label = fields.chars()
    desc = fields.text(nil=True)
    user = fields.user_fk(nil=True)
    links = fields.m2m(ContentLink, nil=True)

    created, updated = fields.dt_cu_pair()
