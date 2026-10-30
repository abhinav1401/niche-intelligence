"""This distribution cannot be switched into a live application by configuration."""

PUBLIC_DEMO_MODE = True


class PublicDemoViolation(PermissionError):
    """An operation is unavailable in the public distribution."""


def blocked(*args, **kwargs):
    raise PublicDemoViolation(
        "Public Demonstration — Synthetic Data: research, network services and persistent changes are disabled."
    )
