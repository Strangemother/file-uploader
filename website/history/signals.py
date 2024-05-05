import django.dispatch

path_access = django.dispatch.Signal()

from . import models

def path_access_signal_callback(sender, **kwargs):
    print('path_access_signal_callback from:', sender)
    models.PathAccess.add(kwargs.get('fullpath'))