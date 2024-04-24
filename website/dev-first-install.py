#!/usr/bin/env python
import os
import sys

from django.core.management import call_command
from trim.execute import read_one_stream_command as read_one

from django.core.management import execute_from_command_line

print('First Install :)')

from trim.models import get_user_model

def main():
    # from django.core.management import call_command
    # call_command('collectstatic', verbosity=3, interactive=False)
    # call_command('migrate', 'myapp', verbosity=3, interactive=False)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings.dev")
    migrate()

    username='admin'
    create_user(username=username, default_pass=True)


def set_default_password(username='admin', word=None):
    m = get_user_model().objects.get(username=username)
    m.set_password(word or 'pass')
    m.save()
    return m


def migrate(*a):
    return execute_from_command_line(("manage.py", 'migrate',) + a)


def create_user(username=None, email=None, default_pass=None):
    # createsuperuser
    #   --username admin
    #   --email admin@localhost
    #   --no-input
    email = email or  f'{username}@localhost'
    parts = ["manage.py", 'createsuperuser',]

    if username is not None:
        parts += ['--username', username,]

    parts += ['--email', email, '--no-input',]


    res = execute_from_command_line(parts)
    if default_pass is not None:
        word = None if default_pass is True else default_pass
        user = set_default_password(username=username, word=word)



if __name__ == "__main__":
    main()



