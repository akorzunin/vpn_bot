class PiVpnException(Exception):
    ...


class UserNotFoundError(PiVpnException):
    ...


class UserAlreadyExistsError(PiVpnException):
    ...


class UserNotDisabledError(PiVpnException):
    ...


class UserNotEnabledError(PiVpnException):
    ...


class UserAlreadyDisabledError(PiVpnException):
    ...
