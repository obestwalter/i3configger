"""Custom errors."""


class I3configgerException(Exception):
    """Main exception with log style string formatting enhancement"""


class BuildError(I3configgerException):
    pass


class ConfigError(I3configgerException):
    pass


class MessageError(I3configgerException):
    pass


class PartialsError(I3configgerException):
    pass


class ParseError(I3configgerException):
    pass


class ContextError(I3configgerException):
    pass


class UserError(I3configgerException):
    """User did something wrong and I can't go on."""
