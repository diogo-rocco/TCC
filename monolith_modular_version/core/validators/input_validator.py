from typing import Dict, Any, List, Optional
import pandas as pd
import re

class InputValidator:

    CEP_DIGITS_RE = re.compile(r"\D+")

    @staticmethod
    def normalize_cep(cep: str) -> Optional[str]:
        if not cep:
            return None
        digits = InputValidator.CEP_DIGITS_RE.sub("", cep)
        if len(digits) != 8 or not digits.isdigit():
            return None
        return digits

    @staticmethod
    def validate(row: pd.Series,  processed_row: Dict[str, Any], errors: List[str]):
        processed_row["order_id"] = row["order_id"]
        processed_row["customer_id"] = row["customer_id"]
        processed_row["cep"] = row["cep"]
        processed_row["requested_date"] = row["requested_date"]

        if not processed_row["order_id"]:
            errors.append("missing_order_id")
        if not processed_row["cep"]:
            errors.append("missing_cep")
        if not processed_row["requested_date"]:
            errors.append("missing_requested_date")
        
        processed_row["cep"] = InputValidator.normalize_cep(processed_row["cep"])
        if not processed_row["cep"]:
            errors.append("invalid_cep_format")