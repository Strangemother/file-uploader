
from django import template
register = template.Library()

@register.filter
def human_bytes(bytes_int):
    try:
        return convert_size(int(bytes_int))
    except ValueError:
        return ''


import math

# @register.simple_tag(takes_context=False)
@register.filter
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])