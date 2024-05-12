from django.core.management.base import BaseCommand, CommandError


from monitor import models, monitor
from pathlib import Path
import traceback

from asgiref.sync import sync_to_async, async_to_sync

from django.conf import settings


def get_config():
    name = settings.DATABASES['monitor']['NAME']
    pn = Path(name)
    ignores = ()
    if pn.exists():
        ignores += (pn.parent.as_posix(), )

    config = {
        'ignore': (
            # "C:/Users/jay/Documents/projects/uploader/website",
            # "C:/Users/jay/Documents/projects/uploader/website/db.sqlite3-journal",
            # "C:/Users/jay/Documents/projects/uploader/website/db.sqlite3",
            # "C:/Users/jay/Documents/projects/uploader/website/monitor_db.sqlite3-journal",
            # "C:/Users/jay/Documents/projects/uploader/website/monitor_db.sqlite3",
        ),
        'ignore_dirs': (
            "C:/Users/jay/AppData/Local/Google/Chrome/User Data/Default",
        ) + ignores
    }

    return config


class Command(BaseCommand):
    help = "Monitor Locations for changes"

    def add_arguments(self, parser):
        parser.add_argument("locations", nargs="+", type=str)

    async def monitor_callback(self, items, **kw):
        print('monitor_callback', len(items), 'updates')
        try:
            r = await self.long_record(items)
            print('returning', r)
            return r
        except Exception as err:
            print('-'*40)
            print(err)
            print('-'*40)
            print(traceback.format_exc())
            # traceback.print_exception(err)
            print('-'*40)
            raise err
        print('monitor_callback End.')

    def handle(self, *args, **options):
        self._path_model_map = {}
        self._action_model_map = {}
        locs = options["locations"]
        callback = self.monitor_callback
        try:
            self.mons = monitor.run_pool(locs, callback, get_config())
            # self.mons = monitor.main_run_pool_gather(locs, callback)
        except KeyboardInterrupt:
            print('Command level KeyboardInterrupt')

    counter = 0
    async def long_record(self, items):
        entries = tuple(Entry(*x) for x in items)
        print('long_record reading', len(items), 'items')
        for entry in entries:
            # print("Reading", entry.as_posix())
            action = await self.get_action_model(entry.action)
            # print('Result action:', action)
            monitor_entry = await self.get_path_model(entry.as_posix())
            record = await self.get_record(action, entry.dt)
            # print('Storing record', record)
            await self.write_entry_record(monitor_entry, record)
        c = self.counter + 1
        self.counter = c
        print('Done. counter', c)
        return c < 4

    @sync_to_async
    def write_entry_record(self, monitor_entry, record):
        monitor_entry.records.add(record)

    @sync_to_async
    def get_record(self, entry_type, dt):
        m, c = models.MonitorRecord.objects.using('monitor').get_or_create(type=entry_type, dt=dt)
        return m

    @sync_to_async
    def get_path_model(self, posix):
        # posix = entry.as_posix()
        am = self._path_model_map.get(posix, None)
        M = models.MonitorEntry
        if am is None:
            m, c = M.objects.using('monitor').get_or_create(fullpath=posix)
            self._path_model_map[posix] = m
            if c:
                print('New Path Model:', posix)
            am = m
        return am

    @sync_to_async
    def get_action_model(self, action):
        al = action.lower()
        am = self._action_model_map.get(al, None)
        if am is None:
            m, c = models.EntryType.objects.using('monitor').get_or_create(name=al)
            self._action_model_map[al] = m
            if c:
                print('New Action Model:', al)
            am = m
        return am


class Entry(object):
    """
        (
            'C:/Users\\jay\\AppData\\Local\\Temp',
            'Updated',
            datetime.datetime(2024, 5, 5, 2, 28, 1, 704265)
        )
    """
    def __init__(self, path, action, dt):
        self.path = Path(path)
        self.action = action
        self.dt = dt

    def as_posix(self):
        return self.path.as_posix()