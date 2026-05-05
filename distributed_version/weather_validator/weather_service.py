import requests
import xml.etree.ElementTree as ET
import unicodedata

class WeatherService:
    BASE_URL = "http://servicos.cptec.inpe.br/XML"

    @staticmethod
    def normalize_city_name(city_name: str) -> str:
        normalized = unicodedata.normalize("NFKD", city_name)
        return "".join([c for c in normalized if not unicodedata.combining(c)])

    @staticmethod
    def get_city_inpe_code(city_name: str, uf: str):
        normalized = WeatherService.normalize_city_name(city_name)
        url = f"{WeatherService.BASE_URL}/listaCidades?city={normalized}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[weather_service] HTTP Error: {response.status_code}")
            return None
        try:
            root = ET.fromstring(response.content)
            for city in root.findall("cidade"):
                name = city.find("nome").text if city.find("nome") is not None else None
                state = city.find("uf").text if city.find("uf") is not None else None
                if name and state and name.lower() == city_name.lower() and state.lower() == uf.lower():
                    return city.find("id").text if city.find("id") is not None else None
            return None
        except ET.ParseError:
            print("[weather_service] Error parsing XML response.")
            return None

    @staticmethod
    def get_forecast(inpe_city_code: str, forecast_date: str):
        url = f"{WeatherService.BASE_URL}/cidade/7dias/{inpe_city_code}/previsao.xml"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[weather_service] HTTP Error: {response.status_code}")
            return None
        try:
            root = ET.fromstring(response.content)
            for dia in root.findall(".//previsao"):
                day_info = {child.tag: child.text for child in dia}
                if day_info.get("dia") == forecast_date:
                    return day_info
            return None
        except ET.ParseError:
            print("[weather_service] Error parsing XML response.")
            return None
