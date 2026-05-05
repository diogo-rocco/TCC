import os
import pandas as pd
from dotenv import load_dotenv

from monolith_with_classes_version.utils.csv import validate_csv, save_dataframe_to_csv
from monolith_with_classes_version.services.database_service import DatabaseService
from monolith_with_classes_version.core.processing import RowProcessor

load_dotenv()

def main():
    df = validate_csv('input/test.csv')

    # Instantiate RowProcessor with the year from the first row
    year = df['requested_date'].dt.year.iloc[0] if not df.empty else None
    db_service = DatabaseService(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
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