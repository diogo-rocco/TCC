import datetime as dt
from typing import Dict, Any, List, Optional
import pandas as pd
from monolith_version.services.database_service import DatabaseService

from TCC.monolith_with_classes_version.core.validators.input_validator import InputValidator
from TCC.monolith_with_classes_version.core.validators.location_validator import LocationValidator
from TCC.monolith_with_classes_version.core.validators.date_validator import DateValidator
from TCC.monolith_with_classes_version.core.validators.weather_validator import WeatherValidator

class RowProcessor:

    def __init__(self, year: int = None, db_service: DatabaseService = None):
        # Initialize feriados and ferr_err for a given year
        self.db_service = db_service
        self.date_validator = DateValidator(year)

    def process_row(self, row: pd.Series) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        processed_row: Dict[str, Any] = {}

        InputValidator.validate(row=row, processed_row=processed_row, errors=errors)
        LocationValidator.validate(processed_row=processed_row, errors=errors)
        self.date_validator.validate(processed_row=processed_row, errors=errors, warnings=warnings)
        WeatherValidator.validate(processed_row=processed_row, errors=errors, warnings=warnings, db_service=self.db_service)

        processed_row["status"] = "OK" if not errors else "ERROR"

        return processed_row
