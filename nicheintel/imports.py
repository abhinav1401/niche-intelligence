"""The public demonstration accepts no uploads or imports."""

from .public_mode import blocked

import_signals = import_trends = import_studio = blocked
