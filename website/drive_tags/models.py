from django.db import models
from trim.models import fields

from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete, pre_save


class PathTag(models.Model):
    """A Single tag, associated to a user.
    """
    label = fields.chars()
    user = fields.user_fk(nil=True)
    slug = fields.slug()
    created, updated = fields.dt_cu_pair()

    def __str__(self):
        return f'"{self.label}" by {self.user}'


from pathlib import Path

class PathTagGroup(models.Model):
    """Associate a _path_ (file or dir) to a set of tags."""
    fullpath = fields.text()
    parent = fields.text()
    name = fields.chars()
    slug = fields.slug()

    tags = fields.m2m(PathTag, nil=True)

    created, updated = fields.dt_cu_pair()

    @property
    def is_dir(self):
        return Path(self.fullpath).is_dir

    def __str__(self):
        c = self.tags.count()
        s = '' if c == 1 else 's'
        return f'"{self.fullpath}" {c} tag{s}'


from trim.models import AutoModelMixin

def get_tags(path):
    p = Path(path).as_posix()
    return PathTag.objects.filter(pathtaggroup__fullpath=p)


class FileUnitPathTagGroupAutoModelMixin(AutoModelMixin):

    def tags(self):
        return get_tags(self.store_path)

    class Meta:
        model_name = "file.FileUnit"


def populate_slug(sender, instance, **kwargs):
    if instance.slug is None:
        instance.slug = slugify(instance.label)


pre_save.connect(populate_slug, PathTag)
# pre_save.connect(populate_slug, PathTagGroup)