# TCC

Validations:
- Normalize destination address (and get municipality identifiers).
    - Call to the https://viacep.com.br/ service to validate CEP and extract address data
- Map to municipality (IBGE) to assign service zone/SLA.
- If delivery date is a holiday, push to next business day.
- (Optional) Weather check to tag risk (e.g., heavy rain) on the requested date.

Requirements

- Pandas
- requests
- urllib3
- mysql-connector-python


Running the project

python3 -m monolith_version.app