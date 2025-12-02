import pandas as pd

REQUIRED_COLUMNS = ['order_id', 'customer_id', 'cep', 'requested_date']

def validate_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, dtype={'cep': str})
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    # Validate date format
    try:
        df['requested_date'] = pd.to_datetime(df['requested_date'], format='%Y-%m-%d', errors='raise')
    except Exception:
        raise ValueError("Column 'requested_date' must be in ISO format YYYY-MM-DD.")
    return df


def save_dataframe_to_csv(df: pd.DataFrame) -> str:
    file_path = 'output/test_out.csv'
    df.to_csv(file_path, index=False)
    return file_path

