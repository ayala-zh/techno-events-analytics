import os
import pandas as pd
from sqlalchemy import create_engine

DB_NAME = "techno_events"
DB_USER = "postgres"
DB_PASSWORD = "0000"
DB_HOST = "localhost"
DB_PORT = "5432"
DATASETS_FOLDER = "datasets"

def import_data():
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    for file in os.listdir(DATASETS_FOLDER):
        if file.endswith(".csv"):
            filepath = os.path.join(DATASETS_FOLDER, file)
            table_name = os.path.splitext(file)[0].lower()

            try:
                # Try reading with auto-detected delimiter
                df = pd.read_csv(filepath, sep=None, engine="python", on_bad_lines="skip")

                df.to_sql(table_name, engine, if_exists="append", index=False)
                print(f"✅ Imported {file} → table '{table_name}' ({len(df)} rows).")

            except Exception as e:
                print(f"❌ Error importing {file}: {e}")

if __name__ == "__main__":
    import_data()
