from app.core.message import ErrorMessage

VALIDATION_MESSAGES = {
    ("username", "missing"): ErrorMessage.USERNAME_REQUIRED,
    ("password", "missing"): ErrorMessage.PASSWORD_REQUIRED,
    ("username", "too_long"): ErrorMessage.USERNAME_MAX_LENGTH,
    ("password", "string_too_short"): ErrorMessage.PASSWORD_MIN_LENGTH,
    ("password", "string_too_long"): ErrorMessage.PASSWORD_MAX_LENGTH,
    ("username", "value_error"): ErrorMessage.USERNAME_FORMAT_EMAIL,
}
