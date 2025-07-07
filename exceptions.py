class RoofError(Exception):
    """Base exception for all roof-related errors."""
    pass

class InvalidDimensionsError(RoofError):
    """Raised when invalid dimensions are provided (non-positive values)."""
    pass

class InvalidSheetSizeError(RoofError):
    """Raised when invalid sheet dimensions are provided."""
    pass

class InvalidPitchError(RoofError):
    pass


class InvalidSheetOverupError(RoofError):
    pass