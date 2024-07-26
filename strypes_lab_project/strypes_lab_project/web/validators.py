from django.core.exceptions import ValidationError


def validate_only_letters_in_name(value):
    if not value.isalpha():
        raise ValidationError('Name should only contain letters.')