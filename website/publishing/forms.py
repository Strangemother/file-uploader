from django import forms
from trim.forms import fields


class PublishContentForm(forms.Form):
    # basket_id = forms.CharField()
    # name = forms.CharField()
    is_public = fields.boolean_false()