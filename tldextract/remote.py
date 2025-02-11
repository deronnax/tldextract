"""tldextract helpers for testing and fetching remote resources."""

from __future__ import annotations

import re
from collections.abc import Callable
from urllib.parse import scheme_chars

inet_pton: Callable[[int, str], bytes] | None
try:
    from socket import AF_INET, inet_pton  # Availability: Unix, Windows.
except ImportError:
    inet_pton = None

IP_RE = re.compile(
    r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
    r"{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
)

scheme_chars_set = set(scheme_chars)


def lenient_netloc(url: str) -> str:
    """Extract the netloc of a URL-like string.

    Similar to the netloc attribute returned by
    urllib.parse.{urlparse,urlsplit}, but extract more leniently, without
    raising errors.
    """
    return (
        _schemeless_url(url)
        .partition("/")[0]
        .partition("?")[0]
        .partition("#")[0]
        .rpartition("@")[-1]
        .partition(":")[0]
        .strip()
        .rstrip(".\u3002\uff0e\uff61")
    )


def _schemeless_url(url: str) -> str:
    double_slashes_start = url.find("//")
    if double_slashes_start == 0:
        return url[2:]
    if (
        double_slashes_start < 2
        or not url[double_slashes_start - 1] == ":"
        or set(url[: double_slashes_start - 1]) - scheme_chars_set
    ):
        return url
    return url[double_slashes_start + 2 :]


def looks_like_ip(
    maybe_ip: str, pton: Callable[[int, str], bytes] | None = inet_pton
) -> bool:
    """Check whether the given str looks like an IP address."""
    if not maybe_ip[0].isdigit():
        return False

    if pton is not None:
        try:
            pton(AF_INET, maybe_ip)
            return True
        except OSError:
            return False
    return IP_RE.fullmatch(maybe_ip) is not None
