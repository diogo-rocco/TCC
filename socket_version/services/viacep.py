from typing import Dict, Any, Optional, Tuple
from . import feriados  # noqa
from ..utils.http import SESSION

_viacep_cache: Dict[str, Dict[str, Any]] = {}

def fetch_viacep(cep: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if cep in _viacep_cache:
        return _viacep_cache[cep], None
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        resp = SESSION.get(url, timeout=SESSION.request_timeout)
        if resp.status_code != 200:
            return None, f"ViaCEP HTTP {resp.status_code}"
        data = resp.json()
        if data.get("erro"):
            return None, "ViaCEP: CEP não encontrado"
        _viacep_cache[cep] = data
        return data, None
    except Exception as e:
        return None, f"ViaCEP error: {e}"
