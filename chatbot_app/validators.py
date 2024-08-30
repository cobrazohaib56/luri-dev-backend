import re

from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError


class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.findall("[A-Z]", password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter, A-Z.")


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not re.findall('[!@#$%&()\-_[\]{};:"./<>?]', password):
            raise ValidationError(
                _("Password must contain at least 1 special character."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Your Password must contain at least 1 special character.")


class NumericCharacterValidator:
    def validate(self, password, user=None):
        if not re.findall("\d", password):
            raise ValidationError(
                _("Password must contain at least 1 numeric character."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Your Password must contain at least 1 numeric character.")
