import phonenumbers

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError


def validate_phone_number(value):
    try:
        phonenumbers.parse(value)
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError(_("Incorrect phone number"))
