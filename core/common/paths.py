"""Common project paths shared outside a single domain owner."""

import os

from core.ml.artifacts import BASE_DIR

LOG_DIR = os.path.join(BASE_DIR, "logs")
