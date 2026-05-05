from typing import Dict, Any, List
from distributed_version.weather_validator.weather_service import WeatherService
from distributed_version.weather_validator.database_service import DatabaseService

class WeatherValidator:

    @staticmethod
    def validate(processed_row: Dict[str, Any], errors: List[str], warnings: List[str], db_service: DatabaseService):
        try:
            processed_row["weather_tag"] = None
            localidade = processed_row.get("localidade")
            uf = processed_row.get("uf")
            delivery_date = processed_row.get("delivery_date")

            if not (localidade and uf and delivery_date):
                return

            inpe_code = db_service.get_city_inpe_code(localidade, uf)
            if not inpe_code:
                inpe_code = WeatherService.get_city_inpe_code(localidade, uf)
                if inpe_code:
                    db_service.insert_city_inpe_code(localidade, uf, inpe_code)

            if not inpe_code:
                errors.append("inpe_code_not_found")
                return

            forecast = WeatherService.get_forecast(inpe_code, delivery_date)
            if forecast:
                processed_row["weather_code"] = forecast.get("tempo")
                processed_row["weather_tag"] = db_service.get_weather_tag(processed_row["weather_code"])
            else:
                warnings.append("date_out_of_forecast_range")
        except Exception as e:
            errors.append(f"weather_exception:{str(e)}")
            print(f"[weather_validator] Error: {e}")
