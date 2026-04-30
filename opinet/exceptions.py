"""Exception hierarchy for the Opinet client."""


class OpinetError(Exception):
    """Base class for all Opinet client errors."""


class OpinetAuthError(OpinetError):
    """Authentication failed or the API key is invalid."""


class OpinetRateLimitError(OpinetError):
    """The API quota or rate limit was exceeded."""


class OpinetInvalidParameterError(OpinetError):
    """A client-side parameter validation error occurred before the HTTP call."""


class OpinetNoDataError(OpinetError):
    """The API returned no data when strict empty handling is enabled."""


class OpinetServerError(OpinetError):
    """The API returned an unexpected response or parsing failed."""


class OpinetNetworkError(OpinetError):
    """A network-level error occurred while calling Opinet."""
