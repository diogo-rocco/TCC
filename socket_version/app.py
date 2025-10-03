import pandas as pd

from socket_version.utils.csv import validate_csv, save_dataframe_to_csv
from socket_version.core.processing import RowProcessor

def main():
    df = validate_csv('input/test.csv')

    # Instantiate RowProcessor with the year from the first row
    year = df['requested_date'].dt.year.iloc[0] if not df.empty else None
    processor = RowProcessor(year=year)

    processed_rows = []
    for _, row in df.iterrows():
        processed_row = processor.process_row(row, enable_weather=True)
        processed_rows.append(processed_row)

    processed_df = pd.DataFrame(processed_rows)
    save_dataframe_to_csv(processed_df)

if __name__ == "__main__":
    main()