from django.db import models
from wagtail.models import Page
# from trim.wagtail.views.generic import StructuredPage
from cinderblock.wagtail.views.generic import StructuredPage
from cinderblock.wagtail import settings_hooks


class CinderblockPage(StructuredPage):
    pass


class HomePage(Page):
    pass
