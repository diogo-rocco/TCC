import datetime as dt
from typing import Dict, Any, List
from distributed_version.date_validator.feriados_service import fetch_feriados, is_holiday, next_business_day

class DateValidator:

    @staticmethod
    def validate(processed_row: Dict[str, Any], errors: List[str], warnings: List[str]):
        processed_row["delivery_date"] = None
        requested_date_str = processed_row.get("requested_date")
        if not requested_date_str:
            return
        try:
            requested_date = dt.date.fromisoformat(requested_date_str)
            feriados, ferr_err = fetch_feriados(requested_date.year)
            if ferr_err or not feriados:
                warnings.append(f"feriados_error:{ferr_err or 'unknown'}")
                feriados = []
            if requested_date.weekday() >= 5 or is_holiday(requested_date, feriados):
                delivery_date = next_business_day(requested_date, feriados)
                warnings.append("requested_date_adjusted_to_next_business_day")
            else:
                delivery_date = requested_date
            processed_row["delivery_date"] = delivery_date.isoformat()
        except Exception as e:
            errors.append(f"feriados_exception:{str(e)}")
            print(f"[date_validator] Error processing date: {e}")
