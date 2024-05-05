import shutil
from pathlib import Path

from django.db import models

from trim.models import fields
from trim.models import AutoModelMixin

from .shared import fs


# Create your models here.
class FileUnit(models.Model):
    name = fields.text()
    suffix = fields.chars()
    file_uuid = fields.chars()
    bytesize = fields.int()
    filepath = fields.text()
    filetype = fields.chars()
    filename = fields.chars()
    internal_name = fields.chars()
    done = fields.bool_false()
    user = fields.user_fk(nil=True)

    # Publishing - if true, then other users can access;
    # access method is separate.
    published = fields.bool_false()

    store_path = fields.text()
    verification = fields.json()
    deletion = fields.json()
    download_count = fields.int(default=0)

    created, updated = fields.dt_cu_pair()

    def as_posix(self):
        return Path(self.store_path).as_posix()

    def __str__(self):
        return f'{self.user} {self.filepath}'

    @property
    def permissions(self):
        o, c = FilePermissionSet.objects.get_or_create(file=self)
        return o

    @property
    def processing(self):
        o, c = FileProcessing.objects.get_or_create(file=self)
        return o

    @property
    def addons(self):
        return FileReader.objects.filter(filetype=self.filetype)


from pydoc import locate

CACHE = {}
def cache_locate(name):
    r = CACHE.get(name)
    if r is None:
        r = locate(name)
        CACHE[name] = r
    return r


class FileReader(models.Model):
    filetype = fields.chars()
    reader_name = fields.chars() # file.readers.audio.AudioReader

    def get_class(self):
        return cache_locate(self.reader_name)


class FilePermissionSet(models.Model):
    file = fields.o2o(FileUnit)
    anonymous_access = fields.bool_false()


class FileProcessing(models.Model):
    file = fields.o2o(FileUnit)
    is_processed = fields.bool_false()
    is_processing = fields.bool_false()


class FileInfoCache(models.Model):
    total_upload_count = fields.int(default=0)
    total_upload_bytes = fields.big_int(default=0)
    total_download_count = fields.int(default=0)
    total_download_bytes = fields.big_int(default=0)
    user = fields.user_o2o(nil=True)

    def __str__(self):
        return f'FileInfoCache {self.user}'


def get_info_cache(user, live=False):
    fic, c = FileInfoCache.objects.get_or_create(user=user)
    return fic


class Options(models.Model):
    name = fields.chars()
    is_default = fields.bool_false()
    allocated_size = fields.int(default=1, help_text='Gigabyte Units')
    max_file_size = fields.int(default=1, help_text='Gigabyte Units')

    def location_disk(self):
        """Return a int for the amount of available space for the
        dest dir
        """
        fsp = Path(fs.location)
        total, used, free = shutil.disk_usage(fsp.drive)
        return {
            'drive': fsp.drive,
            'path': fsp,
            'total': total,
            'used': used,
            'free': free,
        }


class UserOptionsAutoMixin(AutoModelMixin):

    @property
    def info_cache(self):
        return get_info_cache(self)

    def get_options(self):
        return Options.objects.get(is_default=True)

    @property
    def allowances(self):
        return self.get_options()

    class Meta:
        model_name = fields.get_user_model()


