"""
The mail room applies all 'post office' tools into one app. Send your email
through the send function

    from mailroom import mail
    mail.template_send(template_name, email, **props)

Any assigned props are variables for the template.

    from mailroom import mail
    class ContactMessage(models.Model, mail.ModelSendMixin):
        ...

    ts = contactmessage.send_admin_notification(with_cc=True)

"""
from post_office import mail as po_mail
from django.conf import settings
from django.apps import apps

from trim import get_model


class MailTemplateSendModelMixin(object):
    """A cleaner implementation of the 'ModelSendMixin' - eventually a
    replacement"""

    def send_admin_mail(self):
        """Send an email to the admin, from the default email - to the
        meta assigned email.

        mail_template_name is mandatory for a send_admin_mail function

            class Meta:
                mail_template_name = 'quotation_request'
                # mail_object_name = 'quotation'

        """

        # Grab the template name and object name from the meta.
        # debug default name is 'object' and always _model_name_
        template_name = self._meta.mail_template_name
        key_name = 'object'
        replica_name = self._meta.model_name
        if hasattr(self._meta, 'mail_object_name'):
            key_name = self._meta.mail_object_name

        return admin_template_send(template_name, **{replica_name:self, key_name:self})


class ModelSendMixin(object):
    email_template_name = 'web_contact'
    cc_email_template_name  = 'contact_us_cc'

    def get_sender_field(self):
        return self.sender

    def get_email(self):
        sender = self.get_sender_field()
        if sender is not None:
            return sender

        if self.user is not None:
            return self.user.email

        return None

    def send_admin_notification(self, with_cc=False, **kw):
        print('{self.__class__.__name__}::send_admin_notification')
        email = self.get_email()
        cc_myself = getattr(self, 'cc_myself', False)

        if cc_myself is True and (with_cc is True):
            template_send(self.get_cc_email_template_name(), email, email=self, **kw)

        sender = email or 'no-sender@princetonscientific.site'
        # Send an email to the system admins about the new message.
        kw['model'] = self
        return template_send(self.get_email_template_name(), 'SYS_RECIPIENTS',
            email=self, **kw)

    def get_email_template_name(self):
        return self.email_template_name

    def get_cc_email_template_name(self):
        return self.cc_email_template_name



def safe_template_send(template_name, recipients, sender=None, priority=None, bcc=True, **context):
    """Send the email to the recipients as BCC (blind carbon copy), ensuring
    the recipients cannot see each others' email addresses.

    This is a dropin replacement for the `template_send` function

        from mailroom import mail
        mail.template_send('welcome_email', email, user=user)
        mail.safe_template_send('welcome_email', email, user=user)
    """
    M = apps.get_model('post_office.EmailTemplate')
    sender = sender or settings.DEFAULT_FROM_EMAIL

    if isinstance(recipients, str):
        recipients = {
            'SYS_RECIPIENTS': settings.SYS_RECIPIENTS,
        }.get(recipients, recipients)


    reps = None
    bcc_reps = None

    if bcc is True:
        bcc_reps = recipients
    elif bcc is False:
        reps = recipients
    show = reps or bcc_reps
    print(f'Sending email "{template_name}" to recipients:"{show}" - from sender:"{sender}", as BCC: {bcc}')

    try:
        r = po_mail.send(
            recipients=reps,
            sender=None,
            bcc=bcc_reps,
            template=template_name, # Could be an EmailTemplate instance or name
            priority=priority,
            context=context,
        )
        print(f'Result: {r}')
    except M.DoesNotExist:
        # EmailTemplate matching query does not exist.
        error(f'SEND FAIL: mailroom.mail.template_send , {show}, {sender}, {template_name}')
        print(str(context))
        r = False
    return r


def admin_template_send(template_name, **context):
    """Send an email to the admin staff, knowing it can only be sent to SYS receipients
    """

    return template_send(template_name, recipients='SYS_RECIPIENTS', **context)


def is_blocked(email_address):
    BM = get_model('mailroom.BannedMail')
    return BM.objects.filter(email_address=email_address).exists()


def template_send(template_name, recipients, sender=None, priority=None, **context):
    """
    from mailroom import mail
    mail.template_send('welcome_email', email, user=user)
    """
    M = apps.get_model('post_office.EmailTemplate')
    sender = sender or settings.DEFAULT_FROM_EMAIL

    if isinstance(recipients, str):
        recipients = {
            'SYS_RECIPIENTS': settings.SYS_RECIPIENTS,
        }.get(recipients, recipients)

    print(f'Sending email "{template_name}" to recipients:"{recipients}" - from sender:"{sender}"')

    try:
        r = po_mail.send(
            recipients,
            sender,
            template=template_name, # Could be an EmailTemplate instance or name
            priority=priority,
            context=context,
        )
        print(f'Result: {r}')
    except M.DoesNotExist:
        # EmailTemplate matching query does not exist.
        error(f'\n\nSEND FAIL: mailroom.mail.template_send , {recipients}, {sender}, {template_name}\n\n')
        print(str(context))
        r = False
    return r


def send(*a, **kw):
    return po_mail.send(*a, **kw)

