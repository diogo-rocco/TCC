from typing import Dict, Any, List
from distributed_version.location_validator.viacep_service import fetch_viacep

class LocationValidator:

    @staticmethod
    def validate(processed_row: Dict[str, Any], errors: List[str]):
        try:
            viacep = None
            if processed_row.get("cep"):
                viacep, err = fetch_viacep(processed_row["cep"])
                if err or not viacep:
                    errors.append(f"viacep_error:{err or 'unknown'}")

            processed_row["logradouro"] = viacep.get("logradouro") if viacep else None
            processed_row["bairro"] = viacep.get("bairro") if viacep else None
            processed_row["localidade"] = viacep.get("localidade") if viacep else None
            processed_row["uf"] = viacep.get("uf") if viacep else None
            processed_row["ibge_code"] = viacep.get("ibge") if viacep else None
            processed_row["ddd"] = viacep.get("ddd") if viacep else None
        except Exception as e:
            errors.append(f"viacep_exception:{str(e)}")
            print(f"[location_validator] Error: {e}")
