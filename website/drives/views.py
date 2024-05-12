from django.shortcuts import render
from django.urls import reverse

from trim import views
from functools import partial
from pathlib import Path

# from .drives import get_drives_2 as get_drives
from .drives import get_simple_logical as get_drives
from . import forms, models
from trim.models import live


def get_note(path):
    return models.ContentNote.objects.filter(fullpath=path.as_posix()).latest('updated')

def is_public(path):
    p = path.as_posix()
    print('Checking', p)
    return live.publishing.ContentPublish.objects.filter(fullpath=p).exists()

def get_expanded_drives(name):
    s = f'WHERE VolumeName = "{name}"'

    if name.endswith(':') or len(name) == 1:
        s = f'WHERE Name = "{name[0]}:"'
    _drives = get_drives(s)
    return _drives


def get_branch(self):
    return self.relative_to(self.drive).as_posix()[1:]


def rev_parents(self):
    return reversed(self.parents)


Path.branch = get_branch
Path.rev_parents = rev_parents


def resolve_letter(name):
    if name.endswith(':') or len(name) == 1:
        # Just letter
        return name[0]
    drives = get_expanded_drives(name)
    if len(drives) == 0:
        return None
    letter = drives[0]['caption'][0]
    return letter


from drive_tags import tools
from history.signals import path_access

def get_tags(path):
    return tools.get_tags(Path(path))


def get_files(name, path):

    name = resolve_letter(name)

    if path.startswith('/'):
        path = path[1:]

    res = Path(f"{name}:/") / path

    exists = res.exists()
    content_items = ()
    count = 0
    total_size = 0

    if exists:
        content_items = tuple(iter_files(res))
        count = len(content_items)
        total_size = sum(x.bytes() for x in content_items)

    def blank(items):
        return items

    return {
            'path_str': res.as_posix(),
            'path': res,
            'exists': exists,
            'content_items': lambda: content_items,
            'tags': partial(get_tags, res),
            'note': partial(get_note, res),
            'is_public': partial(is_public, res),
            # 'content_items': content_items,
            'count': count,
            'total_size': total_size,
        }

# def get_items(path):
#     return partial(iter_files, path)


def iter_files(path):
    return iter_files_scan(path)
    # return iter_files_path(path)

def as_posix(item):
    return "item" #Path(item).as_posix()

class LesserDir(object):
    def __init__(self, item):
        self.item = item

    def __getattr__(self, key):
        return getattr(self.item, key)

    def as_posix(self):
        return Path(self.path).as_posix()

    def bytes(self):
        return self.item.stat().st_size


def iter_files_path(path):
    res = []
    try:
        for item in path.iterdir():
            item.as_posix = as_posix
            yield item
    except PermissionError as err:
        return str(err)

import os
from scan.scan import list_all

def iter_files_scan(path):
    items = tuple(os.scandir(path))
    try:
        for entry in items:
            yield LesserDir(entry)
    except PermissionError as err:
        return str(err)
    # return list_all(path)


class DriveListView(views.ListView):
    """A List of local disk drives.
    """
    template_name = 'drives/drives_list.html'
    # slug_field = 'name'
    # url_slug_field = 'name'

    def get_queryset(self):
        _drives = get_drives()
        return _drives


class DriveDetailView(views.DetailView):
    """The entry page to a single drive, including a list of
    root files.
    """
    template_name = 'drives/drives_detail.html'
    slug_url_kwarg = 'name'
    slug_field = 'name'

    def get_object(self):
        name = self.kwargs.get('name')
        _drives = get_expanded_drives(name)
        drive = _drives[0] if len(_drives) > 0 else []
        drive['files'] = get_files(name, '.')

        return drive


class DriveContentListView(views.ListView):
    """A List view of content for a directory.
    """
    template_name = 'drives/drives_content_list.html'
    slug_field = 'name'
    url_slug_field = 'name'

    def get_queryset(self):
        name = self.kwargs.get('name')
        path = self.kwargs.get('path')
        _drives = get_files(name, path)
        return [_drives]

    def get(self, *a, **kw):
        print('Drive::DriveContentListView', a, kw)
        fullpath = f"{kw['name']}/{kw['path']}"
        path_access.send(sender=self.__class__, fullpath=fullpath)
        return super().get(*a, **kw)


#from trim.views.serialized import JSONListResponseMixin

from django.core.serializers.python import Serializer
from django.http import JsonResponse


class JsonSerializer(Serializer):

    def get_dump_object(self, obj):
        return {}


class JSONListResponseMixin(object):


    def get_json(self, request, *args, **kwargs):
        result = self.get_queryset()
        # r = serial.serialize([result])
        ctx = {
            self.prop: self.serialize_result(result),
            # self.prop: result
        } if self.prop is not None else result

        return self.render_to_json_response(ctx, **kwargs)

    # def serialize_result(self, result):
    #     serial = self.get_serialiser()
    #     return serial.serialize(result)

    def serialize_result(self, result):
        res = ()
        for item in result:
            files = ()
            for file in item['content_items']():
                f = file.name
                files += (f,)
            o = {
                'path': item['path_str'],
                'items': files,
            }
            res += (o,)
        return res

    def get_serialiser(self):
        serial_data = JsonSerializer()
        serial_data.get_dump_object = self.get_dump_object
        return serial_data

    def get_dump_object(self, obj):
        return {}

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(context)


class JSONDriveContentListView(DriveContentListView, JSONListResponseMixin):
    prop = 'object_list'

    def get(self, request, *args, **kwargs):
        # serial = self.get_serialiser()
        return self.get_json(request, *args, **kwargs)


CACHE = {}
def get_tags(path):
    t = CACHE.get('tools', None)
    if t is None:
        from drive_tags import tools
        CACHE['tools'] = tools
        t = tools

    return t.get_tags(path)


from functools import partial
from mime_list import mediatypes
from trim.models import live


def get_addons(path):
    mime = mediatypes.filter(path.suffix[1:])
    return live.file.FileReader.objects.filter(filetype__in=mime)


class FileDetailView(views.DetailView):
    """A Single file view.
    """
    template_name = 'drives/file_detail.html'
    slug_url_kwarg = 'path'
    slug_field = 'path'

    def get_object(self):
        name = self.kwargs.get('name')
        path = self.kwargs.get('path')

        name = resolve_letter(name)
        res = Path(f"{name}:/") / path
        exists = res.exists()
        # _drives = get_files(name, path)
        return {
            "path": path,
            'path_str': res.as_posix(),
            'path': res,
            'exists': exists,
            'tags': get_tags(res.as_posix()),
            'addons': partial(get_addons, res),
            'note': partial(get_note, res),
            'is_public': partial(is_public, res)
        }


    def get(self, *a, **kw):
        print('Drive::FileDetailView', a, kw)
        fullpath = f"{kw['name']}/{kw['path']}"
        path_access.send(sender=self.__class__, fullpath=fullpath)
        return super().get(*a, **kw)



class DriveExplorerView(views.TemplateView):
    """A Visual display for files (A JS Explorer).
    """
    template_name = 'drives/explorer_view.html'



class ContentNoteListView(views.OrderPaginatedListView):
    default_orderby = '-created'
    model = models.ContentNote
    default_selected_orderby = 'created'
    default_direction = 'asc'
    ordering = f'{default_orderby}'

    min_paginate_by = 20
    max_paginate_by = 200
    paginate_by = 50

    ordering_fields = (
        # ext. val, ext. label, int. key
        ('created', ('Date', 'created')),
        ('fullpath', ('Path', 'fullpath',)),
    )

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     return qs.using('history').filter()#user__pk=get_user(self.request).id)

