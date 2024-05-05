import uuid
import os
from pathlib import Path

from django.shortcuts import render
from django.core.files.storage import default_storage, FileSystemStorage
from django.contrib.auth import get_user

import json

from trim.views.download import streamfile_response
from trim.merge import FileExists, recombine
from trim import views


from trim.views.auth import MissingField, is_staff_or_admin
from trim.views.upload import (
    UploadAssetSuccessView,
    unlink_dir_files,
    UploadChunkView,
    UploadAssetView,
    MergeAssetView,
    get_cache,
)

from . import models

from .shared import fs



class AnonMatchUserOwnedMixin(views.UserOwnedMixin):

    def test_func(self):
        try:
            return super().test_func()
        except MissingField as err:
            pass

        req_user = self.request.user

        # Admins have access.
        is_admin = is_staff_or_admin(req_user) if self.user_allow_staff else False
        active_staff = req_user.is_active and is_admin
        if active_staff:
            return True

        asset = self.get_asset()

        if asset.user is None:
            # Assets uploaded by anon are accessible to anon.
            return True

        if asset.published is False:
            return False

        if req_user.is_anonymous:
            # The user applied anon access.
            return asset.permissions.anonymous_access

        # If open to the public


class FileDetailView(views.DetailView, AnonMatchUserOwnedMixin):
    template_name = "file/file_detail.html"
    model = models.FileUnit
    slug_url_kwarg = 'uuid'
    slug_field = 'file_uuid'
    user_field = 'user'
    user_allow_staff = True

    def get(self, *a, **kw):
        print('FileDetailView', a, kw)
        return super().get(*a, **kw)


class UserFileUnitListView(views.OrderPaginatedListView):
    model = models.FileUnit
    default_orderby = '-updated'
    default_selected_orderby = 'updated'
    default_direction = 'desc'

    ordering_fields = (
        # ext. val, ext. label, int. key
        ('updated', ('Date', 'updated')),
        ('name', ('Name', 'name',)),
        ('size', ('Size', 'bytesize')),
    )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user__pk=get_user(self.request).id)


class UploadAssetSuccessModelView(UploadAssetSuccessView):
    template_name = 'file/upload_success.html'

    def get_asset(self):
        """return the DB model
        """
        file_uuid = self.kwargs['uuid']

        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()
        return info


    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['asset'] = self.get_asset()
        return kwargs


class MergeAssetModelView(MergeAssetView):
    template_name = 'file/merge_view.html'
    skip_step = True

    def get_asset(self):
        """return the DB model
        """
        file_uuid = self.kwargs['uuid']

        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()
        return info


    def get_parts_dir(self):
        """Override to use the db model rather than the dict cache
        """
        file_uuid = self.get_uuid()
        info = self.get_asset()
        name = info.internal_name
        suffix = info.suffix
        username = self.get_current_username()
        make_name = Path(username) / file_uuid
        return make_name

    def perform_all(self, delete_cache=False):
        asset = self.get_asset()
        input_perform_asset = self.resolve_paths()
        # asset['input'] = input_perform_asset

        dir_path = input_perform_asset['path']

        out_path = self.get_out_dir()
        if dir_path.exists():
            output = self.perform(asset, dir_path, out_path)
            # asset['output'] = output
            if delete_cache:
                self.delete_cache(input_perform_asset, asset=asset)
            return True
            # return super().form_valid(form)
        return False

    def perform(self, asset, dir_path, out_path):
        try:
            output_path = recombine(dir_path, out_path)
        except FileExists as err:
            output_path = err.args[0]
            print('ERROR; File already exists', output_path)
        output_path = Path(output_path)
        fs = self.get_fs()

        result = {
            "path": output_path.relative_to(fs.location).as_posix(),
            "exists": output_path.exists(),
            "size": os.path.getsize(output_path),
            'sub_path': output_path.relative_to(out_path).as_posix(),
            'uuid': self.get_uuid(),
        }

        result['output_path'] = Path(result['path']).as_posix()
        result['done'] = True
        result['verification'] = self.verify_file(result, asset)

        asset.done = True
        asset.verification = result['verification']
        asset.store_path = output_path

        asset.save()

        user = asset.user
        if user:
            fic = user.info_cache
            fic.total_upload_count += 1
            fic.total_upload_bytes += asset.bytesize
            fic.save()

        return result

    def verify_file(self, result, asset):
        res = {
            'size': result['size'] == asset.bytesize
        }

        return res

    def delete_cache(self, input_perform_asset, asset):
        """Override to ensure the deleted record is applied to
        the DB model correctly.
        """
        # delete the merge parts.
        print('Delete')
        p = Path(input_perform_asset['path'])
        if p.exists() and p.is_dir():
            # scrub it
            print('Delete', p)
            deleted = unlink_dir_files(p)

            # asset['deletion'] = deleted
            receipt = p / 'delete-receipt.json'
            receipt.write_text(json.dumps(deleted, indent=4))

            asset.deletion = deleted
            asset.save()

        return p.exists() is False


class UploadChunkModelView(UploadChunkView):
    """Override the store chunk view to read the DB reference.
    """

    def generate_store_path(self, data):
        """Override to read the db info.
        Create a new associated record for the upload.

        Return an unchanged store-path
        """
        # returned from the upload asset initial view.
        file_uuid = data['file_uuid']

        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()

        username = self.get_current_username()
        # The mapped name given to the form before the main upload
        name = info.internal_name
        suffix = info.suffix

        # The int chunk index
        index = data['chunk_index']
        # The 'part' defines an extended suffix,
        # to flag this is a partial file.
        part = f".part_{index}"
        filename = f"{name}{suffix}{part}" # received file name
        make_name = Path(username) / file_uuid / filename
        # fs.location is enforced.
        store_path = self.ensure_fullpath(make_name)
        return store_path


class UploadAssetModelCreateView(UploadAssetView):
    template_name = 'upload/upload_view.html'

    def save_asset(self, data):
        fu = self.db_save_asset(data)
        return fu.file_uuid

    def db_save_asset(self, data):
        file_uuid = str(uuid.uuid4())
        filename = data['filename']
        if len(filename) == 0:
            filename = "foo.unknown"

        suffix = Path(data['filepath']).suffix
        name = Path(data['filename']).stem
        # get or create a model.
        fu_models = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            )
        fu_exists = fu_models.exists()

        if fu_exists:
            return fu_models.get()

        user = get_user(self.request)
        user_or_none = None if user.is_anonymous else user

        print('New model', name)
        mdata = {
            'name': name,
            'suffix': suffix,
            'file_uuid':file_uuid,
            'bytesize': data['byte_size'],
            'filepath': data['filepath'],
            'filetype': data['filetype'],
            'filename': filename,
            'internal_name': name,
            'done': False,
            'user': user_or_none,
        }

        fu = models.FileUnit.objects.create(**mdata)
        # for field, value in mdata.items():
        #     setattr(fu, field, value)
        # fu.save()
        return fu


import os
import ctypes

import win32gui
import ctypes as ct
from ctypes import wintypes as w
import win32api

import win32com.shell.shell as shell
import win32event

# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
# https://stackoverflow.com/questions/74872293/shellexecutea-cannot-execute-exe-in-python-with-ctypes-shellexecutea
SW_SHOWNORMAL = 1
shell32 = ct.WinDLL('shell32')
shell32.ShellExecuteA.argtypes = w.HWND, w.LPCSTR, w.LPCSTR, w.LPCSTR, w.LPCSTR, w.INT
shell32.ShellExecuteA.restype = w.HINSTANCE
shell32.ShellExecuteW.argtypes = w.HWND, w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, w.INT
shell32.ShellExecuteW.restype = w.HINSTANCE

import win32gui
from win32con import (SW_SHOW, SW_RESTORE)
import win32process

def get_windows_placement(window_id):
    return win32gui.GetWindowPlacement(window_id)[1]

def set_active_window(window_id):
    if get_windows_placement(window_id) == 2:
        win32gui.ShowWindow(window_id, SW_RESTORE)
    else:
        win32gui.ShowWindow(window_id, SW_SHOW)
    win32gui.SetForegroundWindow(window_id)
    win32gui.SetActiveWindow(window_id)


def find_window_for_pid(pid):
    result = None
    def callback(hwnd, _):
        nonlocal result
        ctid, cpid = win32process.GetWindowThreadProcessId(hwnd)
        if cpid == pid:
            result = hwnd
            return False
        return True
    win32gui.EnumWindows(callback, None)
    return result


import time


class AccessFileView(views.TemplateView):
    template_name = "file/open_file.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        path = Path(self.kwargs['path'])
        name = context.get('filename') or path.name
        # return self.render_to_response(context)
        return streamfile_response(path, name)


class FileOpenView(views.TemplateView):
    template_name = "file/open_file.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        filepath = self.kwargs.get('path')
        if os.path.exists(filepath):
            # os.startfile(filepath)
            # shell32 = ctypes.windll.shell32
            print('Opening', filepath)
            # os.startfile(filepath, show_cmd=5)
            fs_fp =  Path(filepath).name#.replace('/', '\\')
            fs_fpp =  Path(filepath).parent.as_posix().replace('/', '\\')
            # hwin = win32gui.GetDesktopWindow()
            # hwnd = win32gui.FindWindowEx(0,0,0, "Window Title")
            # fw = win32gui.GetForegroundWindow()

            # res = win32api.ShellExecute(0, 'open', fs_fp, None, fs_fpp, 5)
            # res = shell32.ShellExecuteA(0,"open",fs_fp,0,0,5)
            # res = shell32.ShellExecuteW(hwin, 'open', fs_fp, None, None, 1)
            # win32gui.SetForegroundWindow(0)
            #fMask = SEE_MASK_NOASYNC(0x00000100) = 256 + SEE_MASK_NOCLOSEPROCESS(0x00000040) = 64
            info = shell.ShellExecuteEx(fMask = 256 + 64,
                                    lpVerb='open',
                                    lpFile=fs_fp,
                                    lpDirectory=fs_fpp,
                                    nShow=SW_SHOWNORMAL,
                                    # lpParameters='Notes.txt'
                                    )
            hh = info['hProcess']
            # print(dir(info), info)
            # time.sleep(.5)
            # res= win32process.GetProcessId(hh)
            # pid_win = find_window_for_pid(res)
            # ret = win32event.WaitForSingleObject(hh, -1)
            # print(pid_win)
            # win32gui.ShowWindow(hh, SW_RESTORE)
            # win32gui.SetForegroundWindow(hh)
            # set_active_window(pid_win)
            # print(res)
        return self.render_to_response(context)


class DownloadAccessibleFileView(views.TemplateView):
    template_name = "file/download_file.html"

    def get_current_username(self):
        username = self.request.user.username
        if len(username) == 0 and self.request.user.is_anonymous:
            username = 'anonymous'
        return username

    def resolve_fullpath(self, uuid):
        # username = self.get_current_username()
        path = get_cache()[uuid]['output']['path']
        # Resolve with the given path
        root = Path(fs.location)
        out_path = root / path
        sub_path = out_path.resolve().relative_to(root) # for asserting the root
        return out_path
        # return sub_path

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        path = self.resolve_fullpath(self.kwargs['uuid'])
        name = context.get('filename') or path.name
        # return self.render_to_response(context)
        return self.last_stage_handoff(request, path, name, *args, **kwargs)

    def last_stage_handoff(self, request, path, name, *args, **kwargs):
        return streamfile_response(path, name)


class DownloadAccessibleFileModelView(DownloadAccessibleFileView, AnonMatchUserOwnedMixin):
    user_field = 'user'
    user_allow_staff = True

    def get_asset(self):
        """return the DB model
        """
        file_uuid = self.kwargs['uuid']
        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()
        return info

    get_object = get_asset

    def resolve_fullpath(self, uuid):
        # username = self.get_current_username()
        # Resolve with the given path
        asset = self.get_asset()
        path = asset.store_path
        root = Path(fs.location)
        out_path = root / path
        sub_path = out_path.resolve().relative_to(root) # for asserting the root
        return out_path
        # return sub_path

    def last_stage_handoff(self, request, path, name, *args, **kwargs):
        asset = self.get_asset()
        asset.download_count += 1
        asset.save()

        user = request.user

        if user.is_anonymous is False:
            fic = user.info_cache
            fic.total_download_count += 1
            fic.total_download_bytes += asset.bytesize
            fic.save()
        return super().last_stage_handoff(request, path, name, *args, **kwargs)


