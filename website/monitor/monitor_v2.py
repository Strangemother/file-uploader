"""
import monitor
import asyncio
asyncio.run(monitor.start("C:/"))
"""

from multiprocessing.dummy import Pool
from multiprocessing import Process, Queue
from queue import Empty
from functools import partial

from datetime import datetime


import os

import win32event
import win32file
import win32con
import asyncio
import pywintypes
import threading

ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Updated",
    4 : "old name",
    5 : "new name"
}

keep = {}

# Thanks to Claudio Grondi for the correct set of numbers
FILE_LIST_DIRECTORY = 0x0001
top_content = {'step': 0}


def log(*a, **kw):
    print(" > ", *a, **kw)

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue


async def blocking_function(blocking, *args):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, blocking, *args)
    return


def blocking(queue):
    for i in range(n):
        queue.put((id, i))
        time.sleep(s)
    return


def main_run_thread_executor(locs, callback):
    asyncio.run(run_thread_executor(locs, callback))

async def run_thread_executor(locs, callback):

    queue = Queue()

    with ThreadPoolExecutor() as executor:
        tasks = ()
        for loc in locs:
            task_1 = asyncio.create_task(blocking_function(async_afunc, loc, None, queue))
            tasks += (task_1, )
            # task_2 = asyncio.create_task(blocking_function(blocking, queue))

        print_1 = asyncio.create_task(print_queue(queue))

        try:
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            print_1.cancel()
        except KeyboardInterrupt:
            pass


async def print_queue(queue: Queue):
    while True:
        try:
            item = queue.get(block=False)
            print(f"Received from Function {item[0]}: {item[1]}")
            queue.task_done()
        except:
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())

def run_pool(items, callback=None):
    queue = Queue()
    # queue = asyncio.Queue()
    heads = ( (aproc_queue_handler, queue), )
    heads += tuple(
            (x, callback, queue,) for x in items
        )

    with Pool(len(heads)) as pool:
        try:
            print(pool.map(proc_head_astart, heads))
        except KeyboardInterrupt:
            print('Monitor level KeyboardInterrupt')


async def run_pool_gather(items, callback):
    # Schedule three calls *concurrently*:
    queue = Queue()
    # queue = asyncio.Queue()
    await asyncio.gather(
        async_proc_queue_handler(queue),
        *(afunc(x, callback=callback, queue=queue) for x in items)
    )


def main_run_pool_gather(items, callback):
    asyncio.run(run_pool_gather(items, callback), debug=True)


def main_run_pool_executor(items, callback):
    asyncio.run(run_pool_executor(items, callback), debug=True)


import concurrent.futures

async def run_pool_executor(items, callback):
    loop = asyncio.get_running_loop()

    ## Options:

    queue = Queue()
    queue = asyncio.Queue()

    # 1. Run in the default loop's executor:
    # result = await loop.run_in_executor(None, partial(proc_queue_handler, queue))
    # print('default thread pool', result)

     # 2. Run in a custom thread pool:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, partial(proc_queue_handler, queue))
        print('custom thread pool', result)

    # 3. Run in a custom process pool:
    # with concurrent.futures.ProcessPoolExecutor() as pool:
    #     result = await loop.run_in_executor(pool, partial(proc_queue_handler, queue))
    #     print('custom process pool', result)


now = datetime.now

def queue_put(q, *a):
    r = a[0]# + (now(),)
    # print('queue_put', r)
    q.put_nowait(r)


def aproc_queue_handler(queue):
    print('aproc_queue_handler start')
    return asyncio.run(async_proc_queue_handler(queue))


async def async_proc_queue_handler(queue):
    q = queue
    print('async_proc_queue_handler start', q)
    while True:
        print('\nWaiting on queue', q, '\n')
        try:
            item = await q.get()
            print('\n GOT ITEM', item, '\n')
        except Empty:
            print('\nNothing\n')
            item = None
        if item:
            print(f'Working on {item}')
            q.task_done()


def proc_queue_handler(queue):
    q = queue
    print('proc_queue_handler start', q)
    while True:
        print('\nWaiting on queue', q, '\n')
        try:
            item = q.get()
            print('\n GOT ITEM', item, '\n')
        except Empty:
            print('\nNothing\n')
            item = None
        if item:
            print(f'Working on {item}')
            q.task_done()


def proc_head_astart(args):
    if callable(args[0]):
        print('proc_head_astart redirecting functional handler.')
        return args[0](*args[1:])
    return astart(*args)


def astart(watch_dir, callback=None, queue=None):
    print('start', watch_dir)
    # queue = queue or Queue()
    callback = partial(queue_put, queue)
    return asyncio.run(
        afunc(watch_dir, callback=callback, queue=queue))


def afunc(watch_dir, callback=None, queue=None):
    print('start', watch_dir)
    # queue = queue or Queue()
    callback = partial(queue_put, queue)
    return start(watch_dir, callback=callback, queue=queue)


def async_afunc(watch_dir, callback=None, queue=None):
    print('start', watch_dir)
    # queue = queue or Queue()
    callback = partial(queue_put, queue)
    return start(watch_dir, callback=callback, queue=queue)


async def start(watch_dir=None, config=None, callback=None, queue=None):
    """
    import monitor
    import asyncio
    asyncio.run(monitor.start("C:/"))
    """
    log('start')
    global late_task

    config = config or {}
    if watch_dir is None and isinstance(config, tuple):
        watch_dir = config[0]
        config = config[1]

    # scan = config.get('scan', -1) or 0
    #late_task = asyncio.get_running_loop().create_task(late_call())
    #watch_dir = watch_dir
    hDir = await get_hdir(watch_dir)

    await loop(hDir, watch_dir, callback or log_callback, config=config)
    log('monitor.start Done')


async def get_hdir(watch_dir):
    """ Create and return the standard windows "CreateFile" file monitor.
    """
    create_file_args = [
        watch_dir,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None,
    ]

    try:
        hDir = win32file.CreateFile(*create_file_args)
    except pywintypes.error as e:
        # (2, 'CreateFile', 'The system cannot find the file specified.')
        log('monitor.start - FileError', e)
        hDir = None

    return hDir


async def loop(hDir, root_path, callback, config=None):
    log('loop', os.getpid(), hDir)
    log('config', config)
    run = 1
    fails = 0

    while run:

        log('Back into step', root_path)

        try:
            should_continue = await step(hDir, root_path, callback, config=config)
            fails = 0
        except Exception as e:
            log('monitor.loop caught step exception:', str(e))
            traceback.print_exc()
            fails += 1
            should_continue = False if (fails >= 3) else True
            if should_continue is False:
                log(f'\nToo many failures: {fails}. Killing with last failure\n')
                log(e)

        top_content['step'] += 1

        if should_continue is False:
            log('Result is false; stopping monitor.loop for', root_path)
            run = False
            # continue
    log('Loop complete')

async_lock = asyncio.Lock()

async def step(hDir, root_path, callback, config=None):
    #
    # ReadDirectoryChangesW takes a previously-created
    # handle to a directory, a buffer size for results,
    # a flag to indicate whether to watch subtrees and
    # a filter of what changes to notify.
    #
    # NB Tim Juchcinski reports that he needed to up
    # the buffer size to be sure of picking up all
    # events when a large number of files were
    # deleted at once.

    # results = wait(hDir)
    # async for item in results:
    #     log(item)
    #     for action, file in item:
    #         full_filename = os.path.join(path_to_watch, file)
    #         log(full_filename, ACTIONS.get(action, "Unknown"))

    log('>..', end='')
    try:
        results = await wait(hDir)
    except KeyboardInterrupt:
        log('Keyboard cancelled')
        return False

    await asyncio.sleep(.01)

    if results is None:
        log('- Result is None, This may occur if the file is deleted before analysis')
        log(root_path, hDir)
        return False

    if results is async_lock:
        log('Received lock, will wait again')
        return True

    return await step_result_react(results, root_path, callback, config)


import win32process

def set_low_priority():
    # Run this thread at a lower priority to the main message-loop (and printing output)
    # thread can keep up
    win32process.SetThreadPriority(win32api.GetCurrentThread(), win32process.THREAD_PRIORITY_BELOW_NORMAL)


async def wait(hDir, timeout=1000):
    overlapped = pywintypes.OVERLAPPED()
    ce = win32event.CreateEvent(None, 0, 0, None)
    overlapped.hEvent = ce
    try:
        # rc = win32event.WaitForSingleObject(overlapped.hEvent, timeout)
        handles = (ce, )
        # 2nd arg == 0: wait for first, 1 (True), wait for all
        rc = win32event.WaitForMultipleObjects(handles, 0, 1000)

        results = win32file.ReadDirectoryChangesW(
            hDir,
            8192, #1024,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME
            | win32con.FILE_NOTIFY_CHANGE_DIR_NAME
            | win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES
            | win32con.FILE_NOTIFY_CHANGE_SIZE
            | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
            | win32con.FILE_NOTIFY_CHANGE_SECURITY
            | win32con.FILE_NOTIFY_CHANGE_FILE_NAME,
            # ~ win32con.FILE_NOTIFY_CHANGE_CREATION |
            # ~ win32con.FILE_NOTIFY_CHANGE_LAST_ACCESS |
            None,
            None
        )

        #log('watch', results, rc)
        if rc == win32event.WAIT_OBJECT_0:
            # got some data!  Must use GetOverlappedResult to find out
            # how much is valid!  0 generally means the handle has
            # been closed.  Blocking is OK here, as the event has
            # already been set.
            nbytes = win32file.GetOverlappedResult(hDir, overlapped, True)
            if nbytes:
                bits = win32file.FILE_NOTIFY_INFORMATION(buf, nbytes)

                log('nbytes', nbytes, bits)
            else:
                # This is "normal" exit - our 'tearDown' closes the
                # handle.
                # log "looks like dir handle was closed!"
                log('teardown')
                return
        else:
            log('Timeout', hDir, rc)
        #log('return', results)
        return results
    except pywintypes.error as e:
        log('monitor.start - FileError', e)
        return None


async def step_result_react(results, root_path, callback, config):
    log('Iterating', len(results), 'results')
    # clean_actions = ()

    for action, file in results:
        await test_result(root_path, file, action, callback, config)

    if config.get('callback_many'):
        config['callback_many']()

    log('monitor.step fall to end.')
    # return await test_result(root_path, file, action, callback, config)


async def test_result(root_path, file, action, callback, config):

    last = keep.get('last', None)
    full_filename = os.path.join(root_path, file)

    if ignore(action, file, full_filename, config):
        log('x ', full_filename)
        return

    _action = (full_filename, ACTIONS.get(action, "Unknown"))
    # clean_actions += (_action, )

    if _action == last:
        log('Drop Duplicate')
        return

    return await execute_action(_action, file, callback, config)


def log_callback(e, **kw):
    print("log_callback", e, **kw)


def ignore(action, file, full_filename, config):
    _ignore = config.get('ignore', [])
    _ignore_dirs = config.get('ignore_dirs', [])

    if file in _ignore:
       return True

    if full_filename in _ignore:
        return True

    for _dir in _ignore_dirs:
        if file.startswith(_dir): return True
        if full_filename.startswith(_dir): return True


async def execute_action(_action, file, callback, config):
    try:
        v = await execute(_action, callback, config)
        keep['last']  = v
        return v
    except Exception as e:
        log('monitor.step caught exception.', _action, file)
        traceback.print_exc()
        raise e

import traceback

async def execute(result, callback, settings):
    try:
        return callback(result)
    except Exception as e:
        log(f'An exception has occured during callback execution: {e}')
        traceback.print_exc()
        raise e
    # await asyncio.sleep(.3)
    # return result
