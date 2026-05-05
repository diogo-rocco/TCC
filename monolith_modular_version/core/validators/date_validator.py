from typing import Dict, Any, List, Optional
from ...services.feriados_service import fetch_feriados, is_holiday, next_business_day

class DateValidator:
    
    def __init__(self, year: int = None):
        # Initialize feriados and ferr_err for a given year
        self.feriados = None
        self.ferr_err = None
        if year is not None:
            try:
                self.feriados, self.ferr_err = fetch_feriados(year)
            except Exception as e:
                print(f"Unable to fetch holiday list: {e}")

    def validate(self, processed_row: Dict[str, Any], errors: List[str], warnings: List[str]):
        try:
            processed_row["delivery_date"] = None
            if processed_row["requested_date"]:
                if self.ferr_err or not self.feriados:
                    warnings.append(f"feriados_error:{self.ferr_err or 'unknown'}")
                    self.feriados = []
                if processed_row["requested_date"].weekday() >= 5 or is_holiday(processed_row["requested_date"], self.feriados):
                    processed_row["delivery_date"] = next_business_day(processed_row["requested_date"], self.feriados)
                    warnings.append("requested_date_adjusted_to_next_business_day")
                else:
                    processed_row["delivery_date"] = processed_row["requested_date"]
        except Exception as e:
            errors.append(f"feriados_exception:{str(e)}")
            print(f"Error processing holidays for date {processed_row['requested_date']}: {e}")