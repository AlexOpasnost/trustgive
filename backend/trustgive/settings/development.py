"""Development settings — for local dev only."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
CACHALOT_ENABLED = False  # Easier to develop without cache surprises
