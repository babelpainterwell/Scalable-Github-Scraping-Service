# app/core/exceptions.py


class NotFoundError(Exception):
    """Raised when a resource (a user or projects) is not found"""
    pass 

class DatabaseError(Exception):
    """Raised when there is an issue with the database"""
    pass

class ExternalAPIError(Exception):
    """Raised when there is an issue with external API"""
    pass

