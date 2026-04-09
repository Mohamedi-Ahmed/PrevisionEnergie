class ProjectError(Exception):
    """Base exception for the project."""


class StorageError(ProjectError):
    """Raised when a storage operation fails."""


class IngestionError(ProjectError):
    """Raised when an extraction step fails."""


class IngestionConfigurationError(IngestionError):
    """Raised when ingestion settings are missing or invalid."""


class ProcessingError(ProjectError):
    """Raised when a processing step fails."""


class DatabaseError(ProjectError):
    """Raised when a database operation fails."""
