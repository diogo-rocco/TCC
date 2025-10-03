
import re
import datetime as dt
from typing import Dict, Any, List, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..services.viacep import fetch_viacep
from ..services.feriados import fetch_feriados, is_holiday, next_business_day

class RowProcessor:

    def __init__(self, year: int = None):
        # Initialize feriados and ferr_err for a given year
        self.feriados = None
        self.ferr_err = None
        if year is not None:
            try:
                self.feriados, self.ferr_err = fetch_feriados(year)
            except Exception as e:
                print(f"Unable to fetch holiday list: {e}")
    CEP_DIGITS_RE = re.compile(r"\D+")

    @staticmethod
    def normalize_cep(cep: str) -> Optional[str]:
        if not cep:
            return None
        digits = RowProcessor.CEP_DIGITS_RE.sub("", cep)
        if len(digits) != 8 or not digits.isdigit():
            return None
        return digits

    @staticmethod
    def parse_date(s: str) -> Optional[dt.date]:
        try:
            return dt.date.fromisoformat(s.strip())
        except Exception:
            return None

    def process_row(self, row: pd.Series, enable_weather: bool) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        order_id = row["order_id"]
        customer_id = row["customer_id"]
        cep_raw = row["cep"]
        req_date = row["requested_date"]

        feriados = self.feriados
        ferr_err = self.ferr_err

        if not order_id:
            errors.append("missing_order_id")
        if not cep_raw:
            errors.append("missing_cep")
        if not req_date:
            errors.append("missing_requested_date")

        cep = self.normalize_cep(cep_raw)
        if not cep:
            errors.append("invalid_cep_format")

        try:
            viacep = None
            if cep:
                viacep, err = fetch_viacep(cep)
                if err or not viacep:
                    errors.append(f"viacep_error:{err or 'unknown'}")

            logradouro = viacep.get("logradouro") if viacep else None
            bairro = viacep.get("bairro") if viacep else None
            localidade = viacep.get("localidade") if viacep else None
            uf = viacep.get("uf") if viacep else None
            ibge_code = viacep.get("ibge") if viacep else None
            ddd = viacep.get("ddd") if viacep else None
        except Exception as e:
            errors.append(f"viacep_exception:{str(e)}")
            print(f"Error fetching ViaCEP for CEP {cep}: {e}")

        try:
            promised_date = None
            if req_date:
                if ferr_err or not feriados:
                    warnings.append(f"feriados_error:{ferr_err or 'unknown'}")
                    feriados = []
                if req_date.weekday() >= 5 or is_holiday(req_date, feriados):
                    promised_date = next_business_day(req_date, feriados)
                    warnings.append("requested_date_adjusted_to_next_business_day")
                else:
                    promised_date = req_date
        except Exception as e:
            errors.append(f"feriados_exception:{str(e)}")
            print(f"Error processing holidays for date {req_date}: {e}")

        weather_tag = None
        if enable_weather and localidade and uf and promised_date:
            # TODO implementar chamada real para serviço de clima do CPTEC
            seed = (hash(localidade + uf + promised_date.isoformat()) % 3)
            weather_tag = ["CLEAR", "RAIN_RISK", "STORMS_RISK"][seed]

        status = "OK" if not errors else "ERROR"

        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "cep_input": cep_raw,
            "cep_normalized": cep or "",
            "requested_date": req_date.isoformat() if req_date else "",
            "promised_date": promised_date.isoformat() if promised_date else "",
            "logradouro": logradouro or "",
            "bairro": bairro or "",
            "localidade": localidade or "",
            "uf": uf or "",
            "ibge_code": ibge_code or "",
            "ddd": ddd or "",
            "weather_tag": weather_tag or "",
            "status": status,
            "errors": ";".join(errors),
            "warnings": ";".join(warnings),
        }
