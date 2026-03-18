class DomainError(Exception):
    """Business rule violation."""
    pass


class AppError(Exception):
    """Application-level error."""
    pass


class DrivingPortError(Exception):
    """Error in a driving port."""
    pass


class DrivenPortError(Exception):
    """Error in a driven port (infra)."""
    pass


class DrivingAdapterError(Exception):
    """Error in a driving adapter."""
    pass


class DrivenAdapterError(Exception):
    """Error in a driven adapter."""
    pass


class ResourceNotFound(AppError):
    """Entity not found."""
    pass


class ResourceAlreadyExists(AppError):
    """Conflict: entity already exists."""
    pass
