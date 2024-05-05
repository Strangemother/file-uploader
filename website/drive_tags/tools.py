
from . import models

def get_tags(path):
    p = path
    if hasattr(path, 'as_posix'):
        p = path.as_posix()
    return models.PathTag.objects.filter(pathtaggroup__fullpath=p)