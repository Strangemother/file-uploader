from django.db import models
from trim.models import fields

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

