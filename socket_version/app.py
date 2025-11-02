import pandas as pd

from socket_version.utils.csv import validate_csv, save_dataframe_to_csv
from socket_version.core.processing import RowProcessor
from socket_version.services.database_service import MySQLDatabase

def main():
    df = validate_csv('input/test.csv')

    # Instantiate RowProcessor with the year from the first row
    year = df['requested_date'].dt.year.iloc[0] if not df.empty else None
    processor = RowProcessor(year=year)
    db_service = MySQLDatabase(
        host='localhost',
        user='root',
        password='admin',
        database='app'
    )

    for _, row in df.iterrows():
        processed_row = processor.process_row(row, enable_weather=True)
        db_service.insert_order(processed_row)

    db_service.close()

if __name__ == "__main__":
    main()