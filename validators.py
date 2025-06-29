from exceptions import InvalidDimensionsError
from miscellenous import SheetSize, Unit
        

def validate_positive(value: float, name: str) -> None:
        """Validate that a dimension is positive.
        Args:
            value: The value to validate
            name: Name of the parameter for error messages
        Raises:
            InvalidDimensionsError: If value is not positive
        """
       
        if value <= 0:
            raise InvalidDimensionsError(f"{name} must be a positive number.")

def validate_pitch_degrees(pitch_deg: float):
    if not (5 <= pitch_deg <= 60):
        raise InvalidDimensionsError(f"Roof pitch ({pitch_deg}°) must be between 5° and 60°.")
        
def validate_unit(unit: Unit):
    if not isinstance(unit, Unit):
        raise ValueError("Unit must be of type Unit enum (CM, M, FT)")
        
def validate_sheet_size(sheet: SheetSize):
    if not isinstance(sheet, SheetSize):
        raise InvalidSheetSizeError("sheet_size must be a SheetSize")
    if sheet.length <= 0 or sheet.width <= 0:
        raise InvalidSheetSizeError("Sheet length and width must be positive.")
    if sheet.length < 100 or sheet.length > 500:
        raise InvalidSheetSizeError("Sheet length must be realistic (100 - 500 cm).")
        
        

