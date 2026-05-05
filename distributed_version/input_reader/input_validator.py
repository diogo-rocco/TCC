import re
from typing import Dict, Any, List, Optional

class InputValidator:
    CEP_DIGITS_RE = re.compile(r"\D+")

    @staticmethod
    def normalize_cep(cep) -> Optional[str]:
        if not cep:
            return None
        digits = InputValidator.CEP_DIGITS_RE.sub("", str(cep))
        if len(digits) != 8 or not digits.isdigit():
            return None
        return digits

    @staticmethod
    def validate(row: Dict[str, Any], processed_row: Dict[str, Any], errors: List[str]):
        processed_row["order_id"] = row.get("order_id")
        processed_row["customer_id"] = row.get("customer_id")
        processed_row["cep"] = row.get("cep")
        processed_row["requested_date"] = row.get("requested_date")

        if not processed_row["order_id"]:
            errors.append("missing_order_id")
        if not processed_row["cep"]:
            errors.append("missing_cep")
        if not processed_row["requested_date"]:
            errors.append("missing_requested_date")

        processed_row["cep"] = InputValidator.normalize_cep(processed_row["cep"])
        if not processed_row["cep"]:
            errors.append("invalid_cep_format")
