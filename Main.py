import psycopg2
import pandas as pd
from export_excel import export_to_excel

DB_NAME = "techno_events_db"
DB_USER = "postgres"
DB_PASSWORD = "0000"
DB_HOST = "localhost"
DB_PORT = "5432"

def fetch_table_as_df(table_name):
    """Забирает данные из таблицы и возвращает DataFrame"""
    connection = None
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        print(f"Error fetching {table_name}: {e}")
        return pd.DataFrame()
    finally:
        if connection is not None:
            connection.close()

def execute_queries_from_file(file_path):
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()
        print("Connected to database successfully!")

        # Read SQL file safely
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            sql_content = file.read()

        queries = [q.strip() for q in sql_content.split(";") if q.strip()]

        for i, query in enumerate(queries, start=1):
            print(f"\nExecuting Query {i}:")
            cursor.execute(query)
            try:
                results = cursor.fetchall()
                for row in results:
                    print(row)
            except psycopg2.ProgrammingError:
                print("Query executed successfully (no results to display).")

        connection.commit()

    except Exception as e:
        print("Error:", e)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    """execute_queries_from_file("queries.sql")"""

    tables = ["artists", "events"]

    dataframes_dict = {}
    for table in tables:
        df = fetch_table_as_df(table)
        if not df.empty:
            dataframes_dict[table.capitalize()] = df

    if dataframes_dict:
        export_to_excel(dataframes_dict, "report.xlsx")
    else:
        print("No data fetched from database.")
