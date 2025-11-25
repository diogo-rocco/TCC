
import re
import datetime as dt
from typing import Dict, Any, List, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..services.viacep_service import fetch_viacep
from ..services.feriados_service import fetch_feriados, is_holiday, next_business_day
from monolith_version.services.database_service import DatabaseService
from monolith_version.services.weather_service import WeatherService

class RowProcessor:

    def __init__(self, year: int = None, db_service: DatabaseService = None):
        # Initialize feriados and ferr_err for a given year
        self.feriados = None
        self.ferr_err = None
        self.db_service = db_service
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

    def process_row(self, row: pd.Series) -> Dict[str, Any]:
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
            delivery_date = None
            if req_date:
                if ferr_err or not feriados:
                    warnings.append(f"feriados_error:{ferr_err or 'unknown'}")
                    feriados = []
                if req_date.weekday() >= 5 or is_holiday(req_date, feriados):
                    delivery_date = next_business_day(req_date, feriados)
                    warnings.append("requested_date_adjusted_to_next_business_day")
                else:
                    delivery_date = req_date
        except Exception as e:
            errors.append(f"feriados_exception:{str(e)}")
            print(f"Error processing holidays for date {req_date}: {e}")

        weather_tag = None
        if localidade and uf and delivery_date:
            inpe_code_db = self.db_service.get_city_inpe_code(localidade, uf)
            if not inpe_code_db:
                inpe_code = WeatherService.get_city_inpe_code(localidade, uf)
                if inpe_code:
                    self.db_service.insert_city_inpe_code(localidade, uf, inpe_code)
            else:
                inpe_code = inpe_code_db
            if inpe_code:
                forecast = WeatherService.get_forecast(inpe_code, delivery_date.strftime('%Y-%m-%d'))
                if forecast:
                    weather_code = forecast.get("tempo")
                    weather_tag = self.db_service.get_weather_tag(weather_code)
                else:
                    warnings.append("date_out_of_forecast_range")
            else:
                errors.append("inpe_code_not_found")
                # Simulated weather tag based on hash

        status = "OK" if not errors else "ERROR"

        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "cep": cep or "",
            "requested_date": req_date.isoformat() if req_date else "",
            "delivery_date": delivery_date.isoformat() if delivery_date else "",
            "logradouro": logradouro or "",
            "bairro": bairro or "",
            "localidade": localidade or "",
            "uf": uf or "",
            "ibge_code": ibge_code or "",
            "ddd": ddd or "",
            "weather_tag": weather_tag or "",
            "order_status": status,
            "errors": ";".join(errors),
            "warnings": ";".join(warnings),
        }
