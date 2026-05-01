"""Custom password validators for enhanced security."""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class StrongPasswordValidator:
    """
    Şifrenin en az 1 büyük harf, 1 küçük harf, 1 rakam ve 1 özel karakter
    içermesini zorunlu kılar.
    """

    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Şifre en az bir büyük harf içermelidir."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Şifre en az bir küçük harf içermelidir."),
                code='password_no_lower',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Şifre en az bir rakam içermelidir."),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            raise ValidationError(
                _("Şifre en az bir özel karakter içermelidir (!@#$%^&* vb.)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Şifreniz en az 12 karakter olmalı ve en az bir büyük harf, "
            "bir küçük harf, bir rakam ve bir özel karakter içermelidir."
        )
