from pathlib import Path

from django.shortcuts import render
from django.urls import reverse
from trim import views

from . import forms, models

from django.contrib.auth import get_user

class PathTagDetailView(views.DetailView):
    model = models.PathTag
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    # user_field = 'user'
    # user_allow_staff = True


class PathTagListView(views.OrderPaginatedListView):
    default_orderby = 'updated'
    model = models.PathTag
    paginate_by = 50
    min_paginate_by = 50

    ordering_fields = (
        # ext. val, ext. label, int. key
        ('updated', ('Date', 'updated')),
        ('name', ('Name', 'name',)),
    )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user__pk=get_user(self.request).id)


class PathTagUpdateFormView(views.FormView):
    form_class = forms.PathTagUpdateForm
    template_name = 'drives/pathtag_form.html'

    def get_object(self):
        slug = self.kwargs.get('slug')
        return models.PathTag.objects.get(slug=slug)

    def get_initial(self):
        obj = self.get_object()
        return {
            "slug": obj.slug,
            "label": obj.label,
        }

    def get_success_url(self):
        # Back to the tagged file.
        dest = 'tags:list'
        drivepath = reverse(dest)
        return drivepath


    def form_valid(self, form):
        # Assert the posted url is the path url.
        data = form.cleaned_data
        # Perform save.
        obj = self.get_object()
        obj.slug = data['slug']
        obj.label = data['label']
        obj.save()
        return super().form_valid(form)


class PathTagFormView(views.FormView):
    """Add a tag to a path. The label, path are mandatory."""
    form_class = forms.PathTagForm
    template_name = 'drives/pathtag_form.html'

    def get_initial(self):
        return {
            "path": self.kwargs.get('path')
        }

    def record(self, path, label):
        path = Path(path)
        str_path = path.as_posix()
        m, c = models.PathTagGroup.objects.get_or_create(
                fullpath=str_path,
            )
        if c:
            m.parent = path.parent
            m.name = path.name
            m.save()

        user = self.request.user
        tag, cr = models.PathTag.objects.get_or_create(
                label=label,
                user=user,
            )
        m.tags.add(tag)
        return tag

    def get_success_url(self):
        # Back to the tagged file.
        path = Path(self.kwargs.get('path'))
        dest = 'drives:file' if path.is_file else 'drives:content'
        drivepath = reverse(dest, args=(path.as_posix(), ))
        return drivepath

    def form_valid(self, form):
        # Assert the posted url is the path url.
        data = form.cleaned_data
        path = self.kwargs.get('path')
        if data['path'] != path:
            return self.form_invalid(form)
        # Perform save.
        self.record(path, data['label'])
        return super().form_valid(form)
