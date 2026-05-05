import socket
import sys
import pandas as pd
from dotenv import load_dotenv

from distributed_version.input_reader.input_validator import InputValidator
from distributed_version.shared.socket_utils import send_message

load_dotenv()

DATE_VALIDATOR_PORT = 5001

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "input/test.csv"
    df = pd.read_csv(csv_path, dtype={"cep": str})
    df["requested_date"] = pd.to_datetime(df["requested_date"], format="%Y-%m-%d", errors="coerce")

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        rd = row_dict.get("requested_date")
        row_dict["requested_date"] = None if pd.isnull(rd) else pd.Timestamp(rd).strftime("%Y-%m-%d")

        errors = []
        warnings = []
        processed_row = {}
        InputValidator.validate(row=row_dict, processed_row=processed_row, errors=errors)
        processed_row["errors"] = errors
        processed_row["warnings"] = warnings

        try:
            with socket.create_connection(("localhost", DATE_VALIDATOR_PORT)) as sock:
                send_message(sock, processed_row)
                print(f"[input_reader] Sent order {processed_row.get('order_id')}")
        except Exception as e:
            print(f"[input_reader] Failed to send order {processed_row.get('order_id')}: {e}")

if __name__ == "__main__":
    main()
