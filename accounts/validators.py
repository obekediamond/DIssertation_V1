import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    regex = r'^[a-zA-Z]+\/(...)\/(....)'
    message = _(
        'Please enter a username that contains either English letters, '
        'numbers, and @/./+/-/_ special characters or a mix of all'
    )
    flags = re.ASCII
