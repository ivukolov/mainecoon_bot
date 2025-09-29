from pydantic import ValidationError

# class CustomValidationError(ValidationError):
#     """Ошибки валидаций Pydentic"""

class CustomValidationError(ValueError):
    """Ошибки валидаций Pydentic"""