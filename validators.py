from exceptions import InvalidDimensionsError,InvalidPitchError,InvalidSheetSizeError,InvalidPitchError,InvalidSheetOverupError
from miscellenous import SheetSize, Unit,SheetOverup
        

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
    if not (10 <= pitch_deg <= 60):
        raise InvalidPitchError(f"Roof pitch ({pitch_deg}°) must be between 10° and 60°.")
        
def validate_unit(unit: Unit):
    if not isinstance(unit, Unit):
        raise ValueError("Unit must be of type Unit enum (CM, M, FT)")
        
def validate_sheet_size(sheet: SheetSize):
    if not isinstance(sheet, SheetSize):
        raise InvalidSheetSizeError("sheet_size must be a SheetSize")
    if sheet.length <= 0 or sheet.width <= 0:
        raise InvalidSheetSizeError("Sheet length and width must be positive.")
    if sheet.length < 50 or sheet.length > 500:
        raise InvalidSheetSizeError("Sheet length must be realistic (50 - 500 cm).")
        
    if sheet.length<sheet.width:
        raise InvalidSheetSizeError("Sheet length must be realistic ,cannot be less than sheet width.")
        
def validate_sheet_overup(overup: SheetOverup):
    if not isinstance(overup, SheetOverup):
        raise InvalidSheetOverupError("sheet_overup must be a SheetOverup")
    if overup.left_right_overup <= 0 or overup.top_bottom_overup <= 0:
        raise InvalidSheetOverupError("Sheet overups must be positive.")
        
                
        

