"""Report process resource usage separately from learning behavior."""

import sys

try:
    import resource
except ImportError:
    resource = None


def peak_rss_bytes():
    """Return cumulative process peak RSS in bytes, or None when unavailable.

    macOS reports bytes; Linux reports KiB. This includes the process's previous
    work and transition caches, so it is not an isolated learner-memory measure.
    """
    if resource is None:
        return None
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024
