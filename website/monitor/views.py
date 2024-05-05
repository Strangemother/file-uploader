from django.shortcuts import render
from trim import views

from pathlib import Path
from django.contrib.auth import get_user

from . import models


class DefaultMonitorEntryListView(views.ListView):
    model = models.MonitorEntry

    def get_queryset(self):
        qs = super().get_queryset().using('monitor')
        return qs#.filter(user__pk=get_user(self.request).id)


class MonitorEntryListView(views.OrderPaginatedListView):
    """Present a list of history items."""

    default_orderby = '-records__created'
    model = models.MonitorEntry
    default_selected_orderby = 'created'
    default_direction = 'asc'
    ordering = f'{default_orderby}'

    min_paginate_by = 20
    max_paginate_by = 200
    paginate_by = 50

    ordering_fields = (
        # ext. val, ext. label, int. key
        ('created', ('Date', 'records__created')),
        ('fullpath', ('Name', 'fullpath',)),
    )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.using('monitor')#.filter()#user__pk=get_user(self.request).id)


class MonitorEntryDetailListView(MonitorEntryListView):

    def get_object(self):
        qs = super().get_queryset()
        # return self.model.objects.using('monitor')
        return qs.get(id=self.kwargs.get('id'))

    def get_queryset(self):
        qs = super().get_queryset()
        return self.get_object().records.all().order_by("-created")

    def get_context_data(self, **ctx):
        ctx.setdefault('object', self.get_object())
        return super().get_context_data(**ctx)