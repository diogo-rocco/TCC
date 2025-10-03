from typing import Dict, Any, List, Optional, Tuple
import datetime as dt
from ..utils.http import SESSION

_feriados_cache: Dict[int, List[Dict[str, Any]]] = {}

def fetch_feriados(year: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    if year in _feriados_cache:
        return _feriados_cache[year], None
    url = f"https://brasilapi.com.br/api/feriados/v1/{year}"
    try:
        resp = SESSION.get(url, timeout=SESSION.request_timeout)
        if resp.status_code != 200:
            return None, f"Feriados HTTP {resp.status_code}"
        data = resp.json()
        _feriados_cache[year] = data
        return data, None
    except Exception as e:
        return None, f"Feriados error: {e}"

def is_holiday(d: dt.date, feriados: List[Dict[str, Any]]) -> bool:
    dates = {dt.date.fromisoformat(item["date"]) for item in feriados if "date" in item}
    date = dt.date.fromisoformat(d.strftime('%Y-%m-%d'))
    return date in dates

def next_business_day(d: dt.date, feriados: List[Dict[str, Any]]) -> dt.date:
    cur = d
    while True:
        if cur.weekday() >= 5 or is_holiday(cur, feriados):
            cur += dt.timedelta(days=1)
            continue
        return cur
