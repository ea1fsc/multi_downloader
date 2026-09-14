"""Typed errors for the application layer."""


class AppError(Exception):
    """Base application error."""


class ValidationError(AppError):
    """Input or URL validation failed."""


class DownloadError(AppError):
    """Download execution failed."""
