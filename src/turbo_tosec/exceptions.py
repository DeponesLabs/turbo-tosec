"""
Domain-specific exceptions for the Turbo-TOSEC ingestion engine.
"""

class TurboTosecBaseError(Exception):
    """
    Base exception class for all custom Turbo-TOSEC runtime errors.
    Allows upstream layers to catch all engine-specific exceptions using a single block.
    """
    pass

class ConflictingFlagsError(TurboTosecBaseError):
    """
    Raised when the engine receives mutually exclusive operational directives 
    (e.g., both resume and force_new requested simultaneously).
    """
    pass

class VersionMismatchError(TurboTosecBaseError):
    """
    Raised when the TOSEC version detected in the input dataset conflicts 
    with the version already tracked within the existing DuckDB database.
    """
    pass
