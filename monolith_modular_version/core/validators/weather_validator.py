from typing import Dict, Any, List, Optional
from monolith_version.services.weather_service import WeatherService
from monolith_version.services.database_service import DatabaseService

class WeatherValidator:

    @staticmethod
    def validate(processed_row: Dict[str, Any], errors: List[str], warnings: List[str], db_service: DatabaseService):
        try:
            processed_row["weather_tag"] = None
            if processed_row["localidade"] and processed_row["uf"] and processed_row["delivery_date"]:
                inpe_code_db = db_service.get_city_inpe_code(processed_row["localidade"], processed_row["uf"])
                if not inpe_code_db:
                    inpe_code = WeatherService.get_city_inpe_code(processed_row["localidade"], processed_row["uf"])
                    if inpe_code:
                        db_service.insert_city_inpe_code(processed_row["localidade"], processed_row["uf"], inpe_code)
                else:
                    inpe_code = inpe_code_db
                if inpe_code:
                    forecast = WeatherService.get_forecast(inpe_code, processed_row["delivery_date"].strftime('%Y-%m-%d'))
                    if forecast:
                        processed_row["weather_code"] = forecast.get("tempo")
                        processed_row["weather_tag"] = db_service.get_weather_tag(processed_row["weather_code"])
                    else:
                        warnings.append("date_out_of_forecast_range")
                else:
                    errors.append("inpe_code_not_found")
                    # Simulated weather tag based on hash
        except Exception as e:
            errors.append(f"weather_exception:{str(e)}")
            print(f"Error fetching weather for {processed_row['localidade']}, {processed_row['uf']} on {processed_row['delivery_date']}: {e}")