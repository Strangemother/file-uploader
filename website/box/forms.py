from django import forms
from trim.forms import fields


class BoxSimpleForm(forms.Form):
    label = fields.chars()
    desc = fields.text(required=False)


class BoxContentLinkForm(forms.Form):
    uuid = fields.hidden(fields.chars())
    # uuid = fields.chars()
    fullpath = forms.CharField()
    # count = forms.IntegerField(required=False)

    # class Meta:
    #     # fields = ('name',)
    #     # fields = '__all__'
    #     exclude = ('status',)
    #     model = pmodels.Email
