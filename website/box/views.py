from pathlib import Path

from django.shortcuts import render
from django.urls import reverse
from trim import views

from . import forms, models

from django.contrib.auth import get_user


class BoxListView(views.ListView):
    model = models.Box

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user__pk=get_user(self.request).id)


class BoxDetailView(views.DetailView):
    model = models.Box
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'

    # user_field = 'user'
    # user_allow_staff = True

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user__pk=get_user(self.request).id)


class BoxSimpleCreateView(views.FormView):
    form_class = forms.BoxSimpleForm
    template_name = 'box/form.html'

    def form_valid(self, form):
        data = form.cleaned_data

        label = data['label']
        desc = data['desc']

        m = models.Box.objects.create(
                label=label,
                desc=desc,
                user=get_user(self.request),
            )
        self.box = m
        return super().form_valid(form)

    def get_success_url(self):
        # Back to the tagged file.
        dest = 'box:detail'
        uuid = self.box.uuid
        res = reverse(dest, args=(uuid,))
        return res


class BoxContentLinkFormView(views.FormView):
    form_class = forms.BoxContentLinkForm
    template_name = 'box/form.html'

    def get_object(self):
        uuid = self.kwargs.get('uuid')
        return models.Box.objects.get(uuid=uuid)

    def get_initial(self):
        obj = self.get_object()
        return {
            "uuid": obj.uuid,
            # "label": obj.label,
        }

    def get_success_url(self):
        # Back to the tagged file.
        dest = 'box:detail'
        uuid = self.get_object().uuid
        res = reverse(dest, args=(uuid,))
        return res


    def form_valid(self, form):
        # Assert the posted url is the path url.
        data = form.cleaned_data
        # Perform save.
        box = self.get_object()
        path = data['fullpath']
        m, c = models.ContentLink.objects.get_or_create(fullpath=path)
        box.links.add(m)
        return super().form_valid(form)

