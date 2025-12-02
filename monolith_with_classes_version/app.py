import pandas as pd

from monolith_version.utils.csv import validate_csv, save_dataframe_to_csv
from monolith_version.core.processing import RowProcessor
from monolith_version.services.database_service import DatabaseService

def main():
    df = validate_csv('input/test.csv')

    # Instantiate RowProcessor with the year from the first row
    year = df['requested_date'].dt.year.iloc[0] if not df.empty else None
    db_service = DatabaseService(
        host='localhost',
        user='root',
        password='admin',
        database='app'
    )
    processor = RowProcessor(year=year, db_service=db_service)

    for _, row in df.iterrows():
        processed_row = processor.process_row(row)
        order_id = db_service.insert_order(processed_row)
        if processed_row['errors']:
            db_service.insert_error_log(order_id, processed_row['errors'])

    db_service.close()

if __name__ == "__main__":
    main()