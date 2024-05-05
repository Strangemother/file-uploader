from django.db import models

from trim.models import fields

class DataChoices(object):

    def parse_int(self, value):
        return int(value)

    def parse_str(self, value):
        return value

    def choices(self):
        res = ()
        for n in dir(self):
            if n.startswith('__'): continue
            s = 'parse_'
            if n.startswith(s):
                word = n[len(s):]
                choice = (word, word.title(),)
                res += (choice,)
        return res


class EmailTemplateDataOption(models.Model):
    """A single KV for the demo data.
    """
    datachoices = DataChoices()
    key = fields.str(100)
    type = fields.str(choices=datachoices.choices())
    description = fields.text()
    required = fields.bool_true()
    value = fields.str()

    created, updated = fields.dt_cu_pair()

    _short_string = '{self.key} ({self.type}, required={self.required}) "{self.value}"'


class EmailTemplateDemoData(models.Model):
    """A range of settings for an email template; used as a demo with
    dropin parameters.
    """
    name = fields.str(100)
    email_template = fields.fk('post_office.EmailTemplate')
    options = fields.m2m(EmailTemplateDataOption)
    created, updated = fields.dt_cu_pair()

    @classmethod
    def get_by_template(cls, template, name=None):
        return cls.filter_by_template(template, name).get()

    @classmethod
    def filter_by_template(cls, template, name=None):
        qs = cls.objects.filter(email_template=template)
        if name:
            return qs.filter(name=name)
        return qs


class BannedMail(models.Model):
    email_address = fields.email()


from trim.models import AutoModelMixin
from django.template import Context, Template
from django.utils.safestring import mark_safe

from string import Formatter
# import string.Formatter

class SafeFormatter(Formatter):
    def vformat(self, format_string, args, kwargs):
        args_len = len(args)  # for checking IndexError
        tokens = []
        for (lit, name, spec, conv) in self.parse(format_string):
            # re-escape braces that parse() unescaped
            lit = lit.replace('{', '{{').replace('}', '}}')
            # only lit is non-None at the end of the string
            if name is None:
                tokens.append(lit)
            else:
                # but conv and spec are None if unused
                conv = '!' + conv if conv else ''
                spec = ':' + spec if spec else ''
                # name includes indexing ([blah]) and attributes (.blah)
                # so get just the first part
                fp = name.split('[')[0].split('.')[0]
                # treat as normal if fp is empty (an implicit
                # positional arg), a digit (an explicit positional
                # arg) or if it is in kwargs
                if not fp or fp.isdigit() or fp in kwargs:
                    tokens.extend([lit, '{', name, conv, spec, '}'])
                # otherwise escape the braces
                else:
                    tokens.extend([lit, '{{', name, conv, spec, '}}'])
        format_string = ''.join(tokens)  # put the string back together
        # finally call the default formatter
        return Formatter.vformat(self, format_string, args, kwargs)



def read_t(content):
    F = SafeFormatter
    r = filter(None, [i[1] for i in F().parse(F().format(content))])
    return tuple(map(str.strip, r))


class RenderEmailDemoMixin(AutoModelMixin):
    """Apply the render_demo method to the post_office.EmailTemplate class

        from trim import live

        et = live.post_office.EmailTemplate()
        et.render_demo(context)

    """

    def demo_context(self):
        try:
            default = EmailTemplateDemoData.get_by_template(self)
        except EmailTemplateDemoData.DoesNotExist:
            return {}

        def hl(key, v):
            return mark_safe(f'<span class="key" data-key="{key}">{v}</span>')

        opts = {x[0]: hl(x[0], x[1]) for x in default.options.values_list('key', 'value')}
        return opts

    def render_demo(self, context=None):

        subject = self.subject
        message = self.content
        html_message = self.html_content

        opts = self.demo_context()
        _context = Context(context or {})
        _context.update(opts)

        subject = Template(subject).render(_context)
        message = Template(message).render(_context)
        htmlt = Template(html_message)
        html_message = htmlt.render(_context)
        try:
            kk = read_t(self.content)
        except KeyError:
            pass
            kk = None
        return {
            'subject': subject,
            'message': message,
            'html_message': mark_safe(html_message),
            'discovered_fields': kk,
        }


    class Meta:
        model_name = 'post_office.EmailTemplate'


