from django.template.loader import get_template
from django import template
from django.template.loader import render_to_string

from pathlib import Path

register = template.Library()

# @register.filter
# def human_bytes(bytes_int):
    # {{ thing|filter }}


@register.simple_tag(takes_context=True, name='reader.show')
def reader_show(context, filereader_model, filepath=None):
    Class = filereader_model.get_class()
    instance = Class()
    t = get_template(instance.template_name)
    # return render_to_string(instance.template_name, context.flatten())
    return t.render({
          'context': context.flatten(),
          'filepath': Path(filepath),
      })
    # return f"FILE {Class}: {t}"
