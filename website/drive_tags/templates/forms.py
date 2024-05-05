from django import forms
from trim.forms import fields


class PathTagForm(forms.Form):
    path = fields.hidden(forms.CharField())
    label = forms.CharField()
    # count = forms.IntegerField(required=False)

    # class Meta:
    #     # fields = ('name',)
    #     # fields = '__all__'
    #     exclude = ('status',)
    #     model = pmodels.Email
